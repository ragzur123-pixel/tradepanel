# -*- coding: utf-8 -*-
import logging
import pandas as pd
from datetime import datetime, timezone
from db_manager import SovereignDatabase
from data_node import SovereignDataNode
from news_sentinel import NewsSentinel
from optimizer import WalkForwardOptimizer
from broker_dma import BrokerDMA

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    logger.info("Starting Sovereign Node Predator Worker...")
    
    db = SovereignDatabase()
    node = SovereignDataNode()
    
    try:
        # 1. Macro Regime Check & Circuit Breaker
        bist_regime, bist_adx = node.get_market_regime("BIST")
        us_regime, us_adx = node.get_market_regime("US")
        usd_try_trend = node.fetch_usd_try()
        circuit_breaker = node.check_circuit_breaker()
        
        logger.info(f"Macro Check: BIST={bist_regime} (ADX:{bist_adx}), US={us_regime} (ADX:{us_adx}), USD/TRY Trend={usd_try_trend}, Circuit Breaker={circuit_breaker}")

        # 2. Get Watchlist & Portfolio State
        watchlist = db.get_watchlist()
        open_positions = db.get_open_portfolio() # list of tickers
        
        # OPR-03: Retroactive Portfolio Split Adjuster & CAP-05: Time-Decay
        try:
            portfolio_details = db.supabase.table("portfolio").select("id, ticker, entry_date, entry_price, qty").eq("status", "OPEN").execute().data
            if portfolio_details:
                import yfinance as yf
                for pos in portfolio_details:
                    entry_date_str = pos.get("entry_date")
                    if not entry_date_str: continue
                    entry_date = pd.to_datetime(entry_date_str)
                    if entry_date.tz is None:
                        entry_date = entry_date.tz_localize('UTC')
                    else:
                        entry_date = entry_date.tz_convert('UTC')
                        
                    ticker = pos.get("ticker")
                    entry_price = float(pos.get("entry_price") or 0.0)
                    qty = float(pos.get("qty") or 0.0)
                    
                    if entry_price > 0 and qty > 0:
                        try:
                            yf_t = yf.Ticker(ticker)
                            splits = yf_t.splits
                            if not splits.empty:
                                split_dates = pd.to_datetime(splits.index)
                                if split_dates.tz is None:
                                    split_dates = split_dates.tz_localize('UTC')
                                else:
                                    split_dates = split_dates.tz_convert('UTC')
                                splits.index = split_dates
                                recent_splits = splits[splits.index > entry_date]
                                if not recent_splits.empty:
                                    split_ratio = float(recent_splits.prod())
                                    if split_ratio > 0 and split_ratio != 1.0:
                                        new_entry = entry_price / split_ratio
                                        new_qty = int(qty * split_ratio)
                                        db.supabase.table("portfolio").update({
                                            "entry_price": new_entry,
                                            "qty": new_qty,
                                            "entry_date": pd.Timestamp.now(timezone.utc).isoformat()
                                        }).eq("id", pos['id']).execute()
                                        logger.warning(f"OPR-03 SPLIT ADJUST: Adjusted {ticker} for {split_ratio}:1 split. New Entry: {new_entry:.2f}, New Qty: {new_qty}")
                                        entry_price = new_entry
                            
                            # PRTF-02: Retroactive Dividend Adjuster
                            dividends = yf_t.dividends
                            if not dividends.empty:
                                div_dates = pd.to_datetime(dividends.index)
                                if div_dates.tz is None: div_dates = div_dates.tz_localize('UTC')
                                else: div_dates = div_dates.tz_convert('UTC')
                                dividends.index = div_dates
                                recent_divs = dividends[dividends.index > entry_date]
                                if not recent_divs.empty:
                                    total_div = float(recent_divs.sum())
                                    if total_div > 0:
                                        sl = float(pos.get("stop_loss") or 0.0)
                                        tp = float(pos.get("exit_target") or 0.0)
                                        new_entry = max(0.01, entry_price - total_div)
                                        new_sl = max(0.01, sl - total_div) if sl > 0 else sl
                                        new_tp = max(0.01, tp - total_div) if tp > 0 else tp
                                        
                                        db.supabase.table("portfolio").update({
                                            "entry_price": new_entry,
                                            "stop_loss": new_sl,
                                            "exit_target": new_tp,
                                            "entry_date": pd.Timestamp.now(timezone.utc).isoformat()
                                        }).eq("id", pos['id']).execute()
                                        logger.warning(f"PRTF-02 DIVIDEND ADJUST: Adjusted {ticker} for {total_div:.2f} dividend. New Entry: {new_entry:.2f}")
                        except Exception as e:
                            pass
                            
                    days_in_trade = (pd.Timestamp.now(timezone.utc) - entry_date).total_seconds() / 86400
                    if days_in_trade >= 14:
                        logger.warning(f"CAP-05 TIME-DECAY STOP: {ticker} has been open for 14+ days. Flagged as STALE dead money.")
        except Exception as e:
            pass
        
        if not watchlist:
            logger.warning("Watchlist is empty. Add tickers to 'watchlist' table in Supabase.")
            db.update_heartbeat(status="OK", error_msg="Watchlist empty")
            return
            
        #  EXEC-03: Local Walk-Forward Optimization (WFA)
        optimizer = WalkForwardOptimizer()
        optimizer.run_weekend_optimization(watchlist)

        #  HARVEST-01: Statistical Arbitrage Engine (GAMBLER Bucket)
        from pairs_trading_scanner import CorrelationArbitrageEngine
        arb_engine = CorrelationArbitrageEngine()
        gambler_tickers = [entry['ticker'] for entry in watchlist if entry.get('bucket') == 'GAMBLER']
        best_arb_pair = None
        if len(gambler_tickers) >= 2:
            logger.info("HARVEST-01: Running Statistical Arbitrage Scanner on GAMBLER bucket...")
            best_arb_pair = arb_engine.find_best_pair(gambler_tickers)
            if best_arb_pair:
                logger.warning(f" OU STATIONARITY ALERT: Found {best_arb_pair['asset_a']} vs {best_arb_pair['asset_b']} with Z-Score: {best_arb_pair['zscore']}")

        MAX_POSITIONS = 5
        remaining_slots = MAX_POSITIONS - len(open_positions)
        
        #  RISK-02: Global Risk Overlay (Currency Correlation Tracking)
        active_bist = sum(1 for t in open_positions if t.endswith('.IS'))
        active_us = len(open_positions) - active_bist
        MAX_BIST_SLOTS = 3
        MAX_US_SLOTS = 3
        
        logger.info(f"Portfolio State: {len(open_positions)} open positions. Remaining slots: {remaining_slots}")
        logger.info(f"Global Risk Overlay: BIST Exposure={active_bist}/{MAX_BIST_SLOTS}, US Exposure={active_us}/{MAX_US_SLOTS}")

        # DIS-04: 24-Hour Cool-Down Veto
        try:
            recent_cutoff = pd.Timestamp.now(timezone.utc) - pd.Timedelta(hours=24)
            recently_closed_res = db.supabase.table("portfolio").select("ticker, net_pnl").eq("status", "CLOSED").gte("exit_date", recent_cutoff.isoformat()).execute()
            recently_closed_loss = [r['ticker'] for r in recently_closed_res.data if float(r.get('net_pnl') or 0.0) < 0] if recently_closed_res.data else []
        except Exception as e:
            logger.error(f"Failed to fetch recent losses: {e}")
            recently_closed_loss = []

        # CAP-04: Sector Beta-Stacking Mapping
        import yfinance as yf
        open_sectors = {}
        for t in open_positions:
            try:
                sec = yf.Ticker(t).info.get('sector', 'Unknown')
                if sec != 'Unknown':
                    open_sectors[sec] = open_sectors.get(sec, 0) + 1
            except:
                pass
        if open_sectors:
            logger.info(f"Sector Beta-Stacking Profile: {open_sectors}")
        all_limits = []
        paper_trades = []
        
        sentinel = NewsSentinel()
        
        # EXEC-04: Macro Blackout Calendar
        is_macro_blackout = sentinel.check_macro_blackout()
        if is_macro_blackout:
            logger.warning("EXEC-04 MACRO BLACKOUT: High-impact macro event detected (CPI/FOMC). Suspending new entries.")
        
        #  HARVEST-03: Bayesian Self-Auditor
        from bayesian_self_auditor import BayesianSelfAuditor
        auditor = BayesianSelfAuditor(db)
        realized_win_rates = auditor.get_realized_edge()

        # 3. Process Tickers (Bi-Modal)
        now_utc = pd.Timestamp.now(timezone.utc)
        bist_settlement_active = now_utc.hour == 15 and 0 <= now_utc.minute <= 20
        us_settlement_active = (now_utc.hour in [20, 21]) and 0 <= now_utc.minute <= 20

        import concurrent.futures
        
        def fetch_ticker_limits(entry):
            ticker = entry['ticker']
            market = entry.get('market', 'BIST')
            bucket = entry.get('bucket', 'CORE')
            
            if market == 'BIST' and bist_settlement_active:
                return (entry, None, f"EXE-04: BIST Settlement Window Active. Skipping {ticker}")
            if market == 'US' and us_settlement_active:
                return (entry, None, f"EXE-04: US Settlement Window Active. Skipping {ticker}")
            
            logger.info(f"Fetching data for {ticker} ({market}) - {bucket}...")
            try:
                limits = node.calculate_sovereign_limits(ticker, market, bucket)
                return (entry, limits, None)
            except Exception as e:
                return (entry, None, str(e))

        fetched_results = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=15) as executor:
            fetched_results = list(executor.map(fetch_ticker_limits, watchlist))

        for entry, limits, err_msg in fetched_results:
            ticker = entry['ticker']
            market = entry.get('market', 'BIST')
            bucket = entry.get('bucket', 'CORE')
            
            if err_msg:
                if "EXE-04" in err_msg:
                    logger.warning(err_msg)
                else:
                    logger.error(f"Failed to calculate limits for {ticker}: {err_msg}")
                continue
                
            if limits:
                #  FIX 1: State Awareness (Double Dipping Veto)
                if ticker in open_positions:
                    logger.info(f"{ticker} is already in the portfolio. Skiping new signals.")
                    limits['status'] = " ALREADY LONG"
                    all_limits.append(limits)
                    continue

                # DIS-04: 24-Hour Cool-Down Veto
                if ticker in recently_closed_loss:
                    logger.warning(f"DIS-04 COOL-DOWN VETO: {ticker} was recently stopped out. Banning reentry for 24h.")
                    limits['status'] = " 24H COOL-DOWN"
                    all_limits.append(limits)
                    continue

                rejection_reason = None
                
                # DIS-03: Sector Beta-Stacking Veto
                if rejection_reason is None:
                    try:
                        t_sec = yf.Ticker(ticker).info.get('sector', 'Unknown')
                        if t_sec != 'Unknown' and open_sectors.get(t_sec, 0) >= 1:
                            rejection_reason = f"DIS-03 SECTOR VETO: Portfolio already exposed to {t_sec} shock."
                    except:
                        pass
                
                # KAP / Corporate Action Filter (Splits & Dividends invalidate technical math)
                corp_action = sentinel.check_corporate_actions(ticker)
                if corp_action.get("status") == "HIGH_RISK":
                    rejection_reason = corp_action.get("message")
                
                # Institutional Filters
                elif bucket == 'CORE' and limits['current_price'] < limits['sma_200']:
                    rejection_reason = "Price < SMA200"
                
                # ADX Filter for Chop
                else:
                    ticker_regime, ticker_adx = node.get_market_regime(ticker) if market != 'BIST' else (bist_regime, bist_adx)
                    if ticker_adx < 20:
                        rejection_reason = f"ADX {ticker_adx} < 20"
                
                if not rejection_reason and circuit_breaker == 'TRIPPED':
                    rejection_reason = "MACRO CIRCUIT BREAKER TRIPPED"
                    
                # EXEC-04: Macro Blackout Guard
                if not rejection_reason and is_macro_blackout:
                    rejection_reason = "MACRO BLACKOUT: Volatility Event Today (CPI/FOMC)"
                    
                # EXEC-01: Pre-Market Gap Trap Detector
                if not rejection_reason and limits.get('buy_limit') and limits['buy_limit'] > 0:
                    try:
                        t_info = yf.Ticker(ticker).info
                        pm_price = t_info.get('preMarketPrice')
                        if pm_price and pm_price < limits['buy_limit']:
                            rejection_reason = f"PRE-MARKET GAP TRAP: Price ({pm_price}) gap below limit ({limits['buy_limit']})"
                    except:
                        pass
                    
                #  RISK-02: Global Exposure Cap (Correlation/Index Contagion Veto)
                if not rejection_reason and "ACTION ZONE" in limits['status']:
                    if remaining_slots <= 0:
                        rejection_reason = "MAX PORTFOLIO EXPOSURE REACHED"
                    elif market == 'BIST' and active_bist >= MAX_BIST_SLOTS:
                        rejection_reason = "GLOBAL RISK VETO: BIST Correlation Maxed"
                    elif market == 'US' and active_us >= MAX_US_SLOTS:
                        rejection_reason = "GLOBAL RISK VETO: US Correlation Maxed"
                    else:
                        try:
                            t_sec = yf.Ticker(ticker).info.get('sector', 'Unknown')
                            if t_sec != 'Unknown' and open_sectors.get(t_sec, 0) >= 2:
                                rejection_reason = f"BETA-STACKING VETO: Max 2 allowed in {t_sec}"
                        except:
                            pass
                if rejection_reason:
                    logger.info(f"{ticker} rejected by Filter: {rejection_reason}")
                    # Only override status if it's not already a stronger rejection from data_node
                    if "REJECTED" not in limits['status']:
                        limits['status'] = f"REJECTED ({rejection_reason})"
                    
                    # Send to Laboratory (Paper Portfolio) if it's close to limit despite rejection
                    if limits['buy_limit'] > 0 and (limits['current_price'] - limits['buy_limit']) / limits['buy_limit'] < 0.05:
                        paper_trades.append({
                            "ticker": ticker,
                            "reason_for_rejection": rejection_reason,
                            "paper_entry_price": limits['buy_limit']
                        })
                elif "ACTION ZONE" in limits['status']:
                    # We took a slot
                    remaining_slots -= 1
                    if market == 'BIST': active_bist += 1
                    else: active_us += 1
                
                all_limits.append(limits)
            else:
                logger.error(f"Failed to calculate limits for {ticker}")

        # 4. Push to Supabase
        if all_limits:
            limits_df = pd.DataFrame(all_limits)
            db.push_limits(limits_df)
            
            # Push paper trades
            if paper_trades:
                try:
                    db.supabase.table("paper_portfolio").upsert(paper_trades).execute()
                    logger.info(f"Pushed {len(paper_trades)} paper trades to Laboratory.")
                except Exception as e:
                    logger.error(f"Failed to push paper trades: {e}")
            
            #  ADV-02: Seasonality & Time-Decay (Lunchtime Veto)
            current_hour = datetime.now(timezone.utc).hour + 3 # BIST Local Time
            is_lunchtime = 12 <= current_hour < 13
            
            #  EXEC-02 & ADV-04: Real-Time Execution with Microstructure Dynamics
            action_stocks = [s for s in all_limits if s.get("status") in [" ACTION ZONE"]]
            if action_stocks:
                dma = BrokerDMA()
                account_balance = 100000.0 # Mock headless balance
                
                for s in action_stocks:
                    ticker = s['ticker']
                    bucket = s['bucket']
                    market = 'US' if not ticker.endswith('.IS') else 'BIST'
                    
                    if bucket == 'SATELLITE' and is_lunchtime:
                        logger.warning(f"ADV-02 LUNCHTIME VETO: Skipping {ticker} breakout during institutional lunch hour.")
                        continue
                    
                    #  ADV-01 & HARVEST-03: Dynamic Position Sizing using Bayesian Auditor
                    # Replaces theoretical optimisim with empirical realized win-rates.
                    p = realized_win_rates.get(bucket, 0.45)
                    b = 1.2 if bucket == "CORE" else 2.5
                    q = 1 - p
                    kelly_f = max(0, (p - q) / b)
                    half_kelly = kelly_f / 2.0
                    
                    target_capital = account_balance * half_kelly
                    # Cap by Liquidity
                    max_allowed_pos = s['max_pos_size']
                    final_capital = min(target_capital, max_allowed_pos)
                    
                    qty = max(1, int(final_capital / s['current_price']))
                    
                    #  ADV-04: Execution Microstructure Dynamics
                    if bucket == "CORE":
                        exec_algo = "MAKER" # Passive limit
                        limit_price = s['buy_limit']
                    elif bucket == "SATELLITE":
                        exec_algo = "TAKER" # Aggressive limit to sweep liquidity
                        limit_price = s['current_price'] # Cross the spread
                    else:
                        exec_algo = "TWAP" # Slice over time for Gamblers/Low Float
                        limit_price = s['buy_limit']
                    
                    logger.info(f"ADV-01 Kelly Sizing: {ticker} -> Half-Kelly={half_kelly*100:.1f}%, Capital={final_capital:.2f}, Qty={qty}")
                    logger.info(f"ADV-04 Microstructure: Routing {ticker} as {exec_algo}")
                    
                    if market == 'US':
                        success = dma.execute_us_trade(
                            ticker=ticker,
                            action='buy',
                            qty=qty,
                            limit_price=limit_price,
                            stop_price=s['stop_loss'],
                            take_profit=s['sell_target']
                        )
                    else:
                        dma.execute_bist_trade(ticker, 'buy', qty, limit_price)
            
            # EXEC-02: Live Price Telegram Push
            import os
            webhook_url = os.getenv("WEBHOOK_URL")
            if webhook_url:
                msg = " **SOVEREIGN NODE ALERTS** \n\n"
                has_alerts = False

                # 1. New Actionable Entries
                action_stocks = [s for s in all_limits if s.get("status") and "ACTION ZONE" in s.get("status")]
                if action_stocks:
                    has_alerts = True
                    msg += " **NEW LIMITS REACHED**\n"
                    for s in action_stocks:
                        msg += f"• **{s['ticker']}**: Live Price {s['current_price']} crossed Buy Limit {s['buy_limit']}.\n"
                    msg += "\n"
                
                # 2. Active Operations (Risk-Free & Stop Loss)
                try:
                    open_positions_data = db.supabase.table("portfolio").select("*").eq("status", "OPEN").execute().data
                    limit_lookup = {l['ticker']: l for l in all_limits}
                    for pos in open_positions_data:
                        tck = pos.get('ticker')
                        entry_price = float(pos.get('entry_price') or 0.0)
                        ld = limit_lookup.get(tck, {})
                        if not ld:
                            continue
                        current_price = ld.get('current_price', 0)
                        atr = ld.get('atr_14', 0)
                        sl = float(pos.get('stop_loss') or 0.0)
                        
                        rf_target = entry_price + atr
                        if current_price >= rf_target and entry_price > 0:
                            has_alerts = True
                            msg += f" **RISK-FREE TARGET**: {tck} hit {current_price}. Move Stop to Entry ({entry_price}).\n"
                        elif current_price <= sl and sl > 0:
                            has_alerts = True
                            msg += f"<svg width='1em' height='1em' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'><path d='M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z'></path><circle cx='12' cy='12' r='4'></circle></svg> **STOP LOSS HIT**: {tck} dropped to {current_price}. Close Trade.\n"
                except Exception as e:
                    logger.error(f"Error checking active portfolio for alerts: {e}")

                if has_alerts:
                    try:
                        import requests
                        requests.post(webhook_url, json={"content": msg})
                        logger.info("Live Price Telegram Push sent.")
                    except Exception as e:
                        logger.error(f"Failed to send webhook: {e}")

            db.update_heartbeat(
                status="OK", 
                bist_regime=bist_regime, 
                us_regime=us_regime, 
                bist_adx=bist_adx, 
                us_adx=us_adx, 
                usd_try_trend=usd_try_trend,
                circuit_breaker=circuit_breaker
            )
            logger.info("Predator run completed successfully.")
        else:
            logger.error("No valid limits survived the quality gates.")
            db.update_heartbeat(status="ERROR", error_msg="All limits rejected by quality gates")

    except Exception as e:
        logger.critical(f"Critical Worker Failure: {e}")
        db.update_heartbeat(status="ERROR", error_msg=str(e))

if __name__ == "__main__":
    main()
