# -*- coding: utf-8 -*-
import os
import pandas as pd
import yfinance as yf
from isyatirimhisse import fetch_stock_data, fetch_index_data
import logging
from datetime import timezone
import random
import time
from indicators import calculate_sma, calculate_atr, calculate_adx, calculate_mdv, round_to_tick, calculate_cvd
from l2_data_node import L2DataBridge

logger = logging.getLogger(__name__)

class SovereignDataNode:
    def __init__(self):
        self.l2_bridge = L2DataBridge()
        self._benchmarks = {}

    def get_benchmark(self, market, period="1W", interval="15m"):
        ticker = "XU100.IS" if market == "BIST" else "SPY"
        key = f"{ticker}_{period}_{interval}"
        if key not in self._benchmarks:
            try:
                df = yf.download(ticker, period=period, interval=interval, progress=False)
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = df.columns.get_level_values(0)
                df['Close'] = pd.to_numeric(df['Close'], errors='coerce')
                self._benchmarks[key] = df
            except Exception as e:
                logger.error(f"Failed to fetch benchmark {ticker}: {e}")
                self._benchmarks[key] = None
        return self._benchmarks[key]

    def fetch_bist_data(self, ticker, period="2y"):
        """Fetches BIST data using isyatirimhisse with yfinance exponential backoff failover."""
        try:
            start_date = (pd.Timestamp.now() - pd.DateOffset(years=2)).strftime('%d-%m-%Y')
            
            if ticker == "XU100.IS" or ticker == "XU100":
                df = fetch_index_data(
                    indices=["XU100"], 
                    start_date=start_date
                )
                if df is not None and not df.empty:
                    df.rename(columns={'VALUE': 'Close', 'DATE': 'Date'}, inplace=True)
            else:
                df = fetch_stock_data(
                    symbols=[ticker.replace(".IS", "")], 
                    start_date=start_date
                )
                if df is not None and not df.empty:
                    cols_to_keep = ['HGDG_TARIH', 'HGDG_KAPANIS', 'HGDG_MAX', 'HGDG_MIN', 'HGDG_HACIM']
                    df = df[[c for c in cols_to_keep if c in df.columns]].copy()
                    
                    col_map = {
                        'HGDG_KAPANIS': 'Close', 'HGDG_MAX': 'High', 'HGDG_MIN': 'Low', 'HGDG_HACIM': 'Volume', 'HGDG_TARIH': 'Date'
                    }
                    df.rename(columns=col_map, inplace=True)

            if df is not None and not df.empty:
                df = df.loc[:, ~df.columns.duplicated()]
                if 'Date' in df.columns:
                    df.set_index('Date', inplace=True)
                return df
        except Exception as e:
            logger.warning(f"IsYatirim failed for {ticker}: {e}. Trying yfinance with backoff...")
            
        for attempt in range(3):
            try:
                df = yf.download(ticker, period=period, progress=False)
                if df is not None and not df.empty:
                    if isinstance(df.columns, pd.MultiIndex):
                        df.columns = df.columns.get_level_values(0)
                    time.sleep(random.uniform(0.5, 1.5)) # Jitter
                    return df
            except Exception as e:
                logger.warning(f"yfinance attempt {attempt+1} failed for {ticker}: {e}")
                time.sleep((2 ** attempt) + random.uniform(1.0, 3.0))
                
        logger.error(f"All data sources failed for {ticker} after 3 retries.")
        return None

    def fetch_us_data(self, ticker, period="2y"):
        """Fetches US data using yfinance with exponential backoff."""
        import time
        for attempt in range(3):
            try:
                df = yf.download(ticker, period=period, progress=False)
                if df is not None and not df.empty:
                    if isinstance(df.columns, pd.MultiIndex):
                        df.columns = df.columns.get_level_values(0)
                    return df
            except Exception as e:
                logger.warning(f"yfinance attempt {attempt+1} failed for {ticker}: {e}")
                time.sleep(2 ** attempt)
        
        logger.error(f"Failed to fetch US data for {ticker} after retries.")
        return None

    def fetch_usd_try(self):
        """Fetches USD/TRY exchange rate to determine Real Alpha trend."""
        try:
            df = yf.download("USDTRY=X", period="1y", progress=False)
            if df is None or df.empty: return "NEUTRAL"
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            df['Close'] = pd.to_numeric(df['Close'])
            sma50 = calculate_sma(df['Close'], 50).iloc[-1]
            current = df['Close'].iloc[-1]
            return "UP" if current > sma50 else "DOWN"
        except Exception as e:
            logger.error(f"Failed to fetch USD/TRY: {e}")
            return "NEUTRAL"

    def fetch_usd_try_series(self, period="2y"):
        """Fetches raw USD/TRY timeseries for Real Alpha normalization."""
        try:
            df = yf.download("USDTRY=X", period=period, progress=False)
            if df is not None and not df.empty:
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = df.columns.get_level_values(0)
                df['Close'] = pd.to_numeric(df['Close'], errors='coerce')
                df = df.ffill().bfill()
                return df['Close']
        except Exception:
            pass
        return None

    def get_market_regime(self, market="BIST"):
        """Determines macro market regime using BIST-100 (XU100.IS) or SPY."""
        ticker = "XU100.IS" if market == "BIST" else "SPY"
        
        # Always use yfinance for macro indices to ensure we get High/Low for ADX
        try:
            df = yf.download(ticker, period="2y", progress=False)
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
        except Exception as e:
            logger.error(f"Failed to fetch Macro Regime for {ticker}: {e}")
            df = None
        
        if df is None or len(df) < 50: return "NEUTRAL", 0.0
        
        df['Close'] = pd.to_numeric(df['Close'])
        df['SMA_20'] = calculate_sma(df['Close'], 20)
        
        adx = 0.0
        if 'High' in df.columns and 'Low' in df.columns:
            df['High'] = pd.to_numeric(df['High'])
            df['Low'] = pd.to_numeric(df['Low'])
            df['ADX_14'] = calculate_adx(df, 14)
            df['ATR_14'] = calculate_atr(df, 14)
            adx = df['ADX_14'].iloc[-1]
            
            #  HARVEST-02: Institutional Regime Classifier
            from regime_classifier import RegimeClassifier
            clf = RegimeClassifier()
            regime, _ = clf.classify(df)
        else:
            sma50 = calculate_sma(df['Close'], 50).iloc[-1]
            regime = "BULL_MOMENTUM" if df['Close'].iloc[-1] > sma50 else "BEAR_MOMENTUM"
            
        return regime, round(float(adx), 2)

    def check_circuit_breaker(self):
        """Checks VIX for extreme overnight macro shocks."""
        try:
            df = yf.download("^VIX", period="5d", progress=False)
            if df is None or len(df) < 2: return "SAFE"
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            
            df['Close'] = pd.to_numeric(df['Close'])
            current_vix = df['Close'].iloc[-1]
            prev_vix = df['Close'].iloc[-2]
            
            # Circuit Breaker Trips if VIX > 25 OR spiked more than 15% overnight
            if current_vix > 25.0 or (current_vix - prev_vix) / prev_vix > 0.15:
                logger.warning(f"CIRCUIT BREAKER TRIPPED! VIX at {current_vix:.2f}")
                return "TRIPPED"
            return "SAFE"
        except Exception as e:
            logger.error(f"Failed to check VIX: {e}")
            return "SAFE"

    def get_sector_rotation(self):
        """
        Calculates the relative momentum of major BIST sectors over the last 14 days.
        Returns the dominant sector and its return percentage.
        """
        sectors = {
            "Banking": "XBANK.IS",
            "Industrials": "XUSIN.IS",
            "Services": "XUHIZ.IS",
            "Tech": "XUTEK.IS"
        }
        
        momentum = {}
        for name, ticker in sectors.items():
            try:
                # Use history to avoid MultiIndex parsing issues
                stock = yf.Ticker(ticker)
                hist = stock.history(period="1mo")
                if not hist.empty and len(hist) >= 14:
                    close_series = hist['Close']
                    ret = (close_series.iloc[-1] - close_series.iloc[-14]) / close_series.iloc[-14] * 100
                    momentum[name] = float(ret)
            except Exception as e:
                logger.error(f"Failed to fetch {ticker} for sector rotation: {e}")
                
        if not momentum:
            return "Unknown", 0.0
            
        dominant = max(momentum.items(), key=lambda x: x[1])
        return dominant[0], round(dominant[1], 2)

    def calculate_sovereign_limits(self, ticker, market="BIST", bucket="CORE"):
        """Calculates Buy/Sell limits and filters for quality/liquidity."""
        if market == "BIST":
            df = self.fetch_bist_data(ticker)
        else:
            df = self.fetch_us_data(ticker)

        if df is None or len(df) < 200:
            logger.warning(f"Not enough data for {ticker} to calculate SMA200.")
            return None

        # Ensure numeric
        for col in ['Close', 'High', 'Low', 'Volume']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        df = df.ffill().bfill()

        current_price = df['Close'].iloc[-1]
        #  THE FIXES: Derivative Bypass (Warrant Danger)
        if bucket == "GAMBLER":
            return {
                "ticker": ticker,
                "bucket": bucket,
                "current_price": round(float(current_price), 2),
                "buy_limit": 0.0,
                "sell_target": 0.0,
                "stop_loss": 0.0,
                "sma_200": 0.0,
                "sma_50": 0.0,
                "atr_14": 0.0,
                "adv_20": 0.0,
                "max_pos_size": 0.0,
                "status": " GAMBLER (Math Bypassed for Derivatives)",
                "last_updated": pd.Timestamp.now(timezone.utc).isoformat()
            }

        sma200 = calculate_sma(df['Close'], 200).iloc[-1]
        sma50 = calculate_sma(df['Close'], 50).iloc[-1]
        sma20 = calculate_sma(df['Close'], 20).iloc[-1]
        atr14 = calculate_atr(df, 14).iloc[-1]
        
        # MDV Cap & Relative Volume (RVOL)
        #  THE FIXES: Using Median Daily Volume instead of Average to strip fake dark-pool block trades.
        mdv20 = 0.0
        max_pos_size = 0.0
        rvol = 1.0
        if 'Volume' in df.columns:
            mdv20 = calculate_mdv(df, 20).iloc[-1]
            max_pos_size = mdv20 * 0.01
            today_vol = df['Volume'].iloc[-1]
            
            # Intraday Pro-Rata Volume Adjustment to prevent RVOL handicap
            now_utc = pd.Timestamp.now(timezone.utc)
            if market == "BIST":
                loc_tz = 'Europe/Istanbul'
                market_open = 10.0
                market_close = 18.0
            else:
                loc_tz = 'America/New_York'
                market_open = 9.5
                market_close = 16.0
                
            loc_time = now_utc.tz_convert(loc_tz)
            current_hour = loc_time.hour + loc_time.minute / 60.0
            
            # Only prorate if we are currently inside trading hours on a weekday
            if loc_time.weekday() < 5 and market_open < current_hour < market_close:
                elapsed_fraction = (current_hour - market_open) / (market_close - market_open)
                # Cap minimum fraction at 0.05 to avoid division by near-zero at open
                elapsed_fraction = max(0.05, elapsed_fraction)
                today_vol_projected = today_vol / elapsed_fraction
            else:
                today_vol_projected = today_vol
                
            rvol = today_vol_projected / mdv20 if mdv20 > 0 else 1.0

        #  HARVEST-05: Fundamental Mirage Detector (Liquidity Vacuum)
        vol_mean = df['Volume'].rolling(window=20).mean().iloc[-1]
        vol_std = df['Volume'].rolling(window=20).std().iloc[-1]
        vol_z = (today_vol_projected - vol_mean) / vol_std if vol_std > 0 else 0.0
        
        # If stock is 30% above its 200 SMA but volume is dying (Z < -1.5), it's a Mirage.
        mirage_veto = False
        if current_price > sma200 * 1.30 and vol_z < -1.5:
            mirage_veto = True
            logger.warning(f"HARVEST-05 MIRAGE DETECTED: {ticker} is 30%+ above SMA200 on collapsing volume (Z: {vol_z:.2f})")

        #  THE FIXES: Dynamic Parameters (Volatility Regime Expansion - RISK-04)
        atr14_series = calculate_atr(df, 14)
        atr14 = atr14_series.iloc[-1]
        atr_pct = (atr14_series / df['Close']) * 100
        current_atr_p = atr_pct.iloc[-1]
        hist_atr = atr_pct.tail(100)
        p_rank = (hist_atr < current_atr_p).mean() * 100
        
        if p_rank < 30:
            sl_mult, tp_ratio = 1.8, 4.0
        elif p_rank > 80:
            sl_mult, tp_ratio = 3.5, 2.5
        else:
            sl_mult, tp_ratio = 2.5, 3.0
            
        base_mult = 0.5 if bucket == "CORE" else 1.0
        dynamic_multiplier = round(base_mult * sl_mult, 2)
        
        buy_target = sma20 - (dynamic_multiplier * atr14)
        
        #  OPR-04: Regime Risk Overlay (Adaptive Target Scaling)
        # We must adjust tp_ratio based on the Macro Regime to ensure targets reflect reality.
        try:
            from regime_classifier import RegimeClassifier
            clf = RegimeClassifier()
            regime_ticker = "XU100.IS" if market == "BIST" else "SPY"
            regime_df = self.fetch_bist_data(regime_ticker) if market == "BIST" else self.fetch_us_data(regime_ticker)
            if regime_df is not None and len(regime_df) >= 200:
                regime, _, _ = clf.classify(regime_df)
                if regime == "BEAR_RALLY" or regime == "BEAR_CRASH":
                    tp_ratio = tp_ratio * 0.7 # Tighten targets in bear regimes
                elif regime == "PARABOLIC_BULL":
                    tp_ratio = tp_ratio * 1.5 # Expand targets in euphoria
        except Exception as e:
            pass
        
        
        #  RISK-03 & EXEC-04: Dynamic Transaction Cost Analysis (TCA)
        # Replaces hardcoded 10bps slippage with real-time Bid-Ask spread width.
        dynamic_drag = self.l2_bridge.get_dynamic_spread(ticker, market)
        buy_limit = round_to_tick(buy_target * (1 + dynamic_drag), market) # Slipped entry
        
        # ALPH-03: Institutional Volume Node (VWAP)
        if 'Volume' in df.columns and df['Volume'].tail(20).sum() > 0:
            recent_df = df.tail(20)
            vwap_20 = (recent_df['Close'] * recent_df['Volume']).sum() / recent_df['Volume'].sum()
            # If our buy_limit is floating above the institutional average price, pull it down to the volume node
            if buy_limit > vwap_20:
                buy_limit = round_to_tick(vwap_20 * (1 + dynamic_drag), market)
        
        raw_target = buy_limit + (tp_ratio * atr14)
        sell_target = round_to_tick(raw_target * (1 - dynamic_drag), market) # Slipped exit
        
        #  RISK-01: Intraday Circuit Breakers (Volatility-Floor Stops)
        v_floor = current_price * df['Close'].pct_change().rolling(window=20).std().iloc[-1]
        sl_dist = max(atr14 * sl_mult, v_floor * 3.0)
        
        # FIX: Remove chandelier_stop for entry targets, it causes stop loss to be above entry price.
        naive_stop = buy_limit - sl_dist
        dynamic_stop = naive_stop # Structural stops will be added post-execution
        
        stop_loss = round_to_tick(dynamic_stop * (1 - dynamic_drag), market) # Slipped stop exit

        from geometry import calculate_fvg
        
        fvgs = calculate_fvg(df)
        bullish_fvgs = [f for f in fvgs if f['type'] == 'BULLISH_FVG' and f['top'] <= current_price]
        
        if bullish_fvgs:
            closest_fvg = bullish_fvgs[-1]
            liquidity_zone_top = round_to_tick(closest_fvg['top'], market)
            liquidity_zone_bot = round_to_tick(closest_fvg['bottom'], market)
        else:
            # Fallback to an ATR-based cushion around the buy_limit
            liquidity_zone_top = round_to_tick(buy_limit + (0.5 * atr14), market)
            liquidity_zone_bot = round_to_tick(buy_limit - (0.5 * atr14), market)

        # Relative Strength (RS) Divergence Tracking
        rs_divergence = False
        benchmark_df = self.get_benchmark(market, period="1mo", interval="15m")
        if benchmark_df is not None and not benchmark_df.empty and len(benchmark_df) >= 20 and len(df) >= 20:
            bench_return = (benchmark_df['Close'].iloc[-1] - benchmark_df['Close'].iloc[-20]) / benchmark_df['Close'].iloc[-20]
            asset_return = (df['Close'].iloc[-1] - df['Close'].iloc[-20]) / df['Close'].iloc[-20]
            
            # If benchmark drops > 0.5% but asset outperforms by > 1.0%
            if bench_return < -0.005 and asset_return > (bench_return + 0.01):
                rs_divergence = True

        status = " NEUTRAL"
        dist = (current_price - buy_limit) / buy_limit * 100
        
        # PROD-04: Dual-Oracle Data Redundancy
        prev_price = df['Close'].iloc[-2] if len(df) > 1 else current_price
        price_change = abs(current_price - prev_price) / prev_price if prev_price > 0 else 0
        
        is_data_poisoned = False
        if price_change > 0.15:
            try:
                import requests
                import re
                symbol = ticker.replace('.IS', '')
                exchange = "IST" if market == "BIST" else "NASDAQ"
                url = f"https://www.google.com/finance/quote/{symbol}:{exchange}"
                headers = {'User-Agent': 'Mozilla/5.0'}
                res = requests.get(url, headers=headers, timeout=3)
                if res.status_code == 200:
                    match = re.search(r'class="YMlKec fxKbKc"[^>]*>([^<]+)</div>', res.text)
                    if match:
                        g_price_str = match.group(1).replace(',', '').replace('₺', '').replace('$', '').strip()
                        g_price = float(g_price_str)
                        if abs(g_price - current_price) / current_price > 0.05:
                            is_data_poisoned = True
                    else:
                        is_data_poisoned = True
                else:
                    is_data_poisoned = True
            except:
                is_data_poisoned = True 
        is_volume_climax = rvol > 2.5 and current_price < prev_price
        is_block_anomaly = rvol > 5.0 and current_price >= prev_price
        
        # Algorithmic Killzones
        current_time_utc = pd.Timestamp.now(timezone.utc)
        killzone_active = False
        kz_name = ""
        
        try:
            if market == "BIST":
                local_time = current_time_utc.tz_convert('Europe/Istanbul')
                float_time = local_time.hour + local_time.minute / 60.0
                if 10.0 <= float_time <= 11.0:
                    killzone_active = True
                    kz_name = "OPENING DRIVE"
                elif 17.5 <= float_time <= 18.0:
                    killzone_active = True
                    kz_name = "MOC IMBALANCE"
            elif market == "US":
                local_time = current_time_utc.tz_convert('America/New_York')
                float_time = local_time.hour + local_time.minute / 60.0
                if 9.5 <= float_time <= 10.5:
                    killzone_active = True
                    kz_name = "OPENING DRIVE"
                elif 15.5 <= float_time <= 16.0:
                    killzone_active = True
                    kz_name = "MOC IMBALANCE"
        except Exception:
            pass
        
        #  DISCRETIONARY-01: The Intraday Blindspot Veto
        # If the stock gapped down or crashed intraday by > 3%, immediately reject to prevent human bag-holding on stale daily limits.
        is_gap_down_trap = current_price < prev_price * 0.97
        
        gross_alpha_pct = (sell_target - buy_limit) / buy_limit if buy_limit > 0 else 0
        is_low_edge = gross_alpha_pct < 0.015

        #  ADV-03: BIST-Specific Hedging (The Lira Veto)
        is_devaluation_mirage = False
        if market == "BIST":
            usd_try = self.fetch_usd_try_series()
            if usd_try is not None:
                # Align dates
                aligned_usd = usd_try.reindex(df.index).ffill().bfill()
                real_usd_close = df['Close'] / aligned_usd
                
                # Check nominal uptrend vs real downtrend
                nominal_sma50 = sma50
                real_sma50 = calculate_sma(real_usd_close, 50).iloc[-1]
                
                if current_price > nominal_sma50 and real_usd_close.iloc[-1] < real_sma50:
                    is_devaluation_mirage = True

        #  THE FIXES: Fundamental Check (Garbage-In, Garbage-Out Prevention)
        pe_rejected = False
        earnings_veto = False
        
        try:
            yf_ticker = yf.Ticker(ticker)
            
            # The Volatility Crush Veto (Earnings Trap)
            calendar = yf_ticker.calendar
            if calendar and 'Earnings Date' in calendar and len(calendar['Earnings Date']) > 0:
                next_earnings = calendar['Earnings Date'][0]
                if next_earnings is not None:
                    earnings_date = pd.Timestamp(next_earnings).tz_localize(None)
                    today = pd.Timestamp.now().tz_localize(None)
                    days_to_earnings = (earnings_date - today).days
                    if 0 <= days_to_earnings <= 3:
                        earnings_veto = True

            # PROD-02: Corporate Action Suppressor
            corp_action_veto = False
            try:
                dividends = yf_ticker.dividends
                splits = yf_ticker.splits
                today_tz_naive = pd.Timestamp.now().tz_localize(None)
                if not dividends.empty:
                    last_div_date = pd.to_datetime(dividends.index[-1]).tz_localize(None)
                    if 0 <= (today_tz_naive - last_div_date).days <= 2:
                        corp_action_veto = True
                if not splits.empty:
                    last_split_date = pd.to_datetime(splits.index[-1]).tz_localize(None)
                    if 0 <= (today_tz_naive - last_split_date).days <= 2:
                        corp_action_veto = True
            except:
                pass

            if bucket == "CORE":
                stock_info = yf_ticker.info
                pe_ratio = stock_info.get("trailingPE")
                pb_ratio = stock_info.get("priceToBook")
                
                # Soft PE Check: We only reject if we definitively have data and it's terrible.
                if pe_ratio is not None and (pe_ratio < 0 or pe_ratio > 100):
                    pe_rejected = True
                elif pe_ratio is None and pb_ratio is not None and pb_ratio < 0:
                    pe_rejected = True
                    
            time.sleep(random.uniform(0.3, 1.0)) # Jitter info fetch
        except Exception as e:
            pass # Fail silently if yfinance info breaks
        
        if is_data_poisoned:
            status = " REJECTED (DATA ANOMALY)"
        elif is_low_edge:
            status = f" REJECTED (LOW EDGE: {gross_alpha_pct*100:.1f}%)"
        elif is_volume_climax and dist <= 2:
            status = " REJECTED (VOLUME CLIMAX DUMP)"
        elif earnings_veto:
            status = " REJECTED (IMMINENT EARNINGS VOLATILITY)"
        elif corp_action_veto:
            status = " REJECTED (CORPORATE ACTION: Ex-Div/Split Veto)"
        elif pe_rejected:
            status = " REJECTED (FUNDAMENTALLY UNSAFE: Extreme P/E)"
        elif is_devaluation_mirage:
            status = " REJECTED (LIRA VETO: Devaluation Mirage)"
        elif mirage_veto:
            status = " REJECTED (LIQUIDITY VACUUM: Fundamental Mirage)"
        elif dist <= 0: 
            status = " ACTION ZONE"
        elif dist <= 2: 
            status = " APPROACHING"
            
        # ALPH-02: Multi-Timeframe Fractal Alignment
        yf_t = yf.Ticker(ticker)
        if "ACTION ZONE" in status:
            try:
                wk_df = yf_t.history(period="1y", interval="1wk")
                if not wk_df.empty and len(wk_df) >= 20:
                    wk_close = wk_df['Close'].iloc[-1]
                    wk_sma20 = wk_df['Close'].rolling(window=20).mean().iloc[-1]
                    if wk_close < wk_sma20:
                        status = " REJECTED (FRACTAL VETO: Weekly Trend Bearish)"
            except Exception:
                pass
                
        # ALPH-01: Alpha Conviction Score
        alpha_score = 0
        if "ACTION ZONE" in status or "APPROACHING" in status:
            if rvol > 1.5: alpha_score += 25
            elif rvol > 1.0: alpha_score += 15
            
            if current_price > sma50: alpha_score += 25
            if current_price > sma200: alpha_score += 15
            
            df['ADX_14'] = calculate_adx(df, 14)
            if 'ADX_14' in df.columns:
                adx = df['ADX_14'].iloc[-1]
                if adx > 25: alpha_score += 15
            
            try:
                if market == "BIST":
                    dom_sec, _ = self.get_sector_rotation()
                    stock_sec = yf_t.info.get('sector', '').lower()
                    
                    # Yahoo Finance uses 'financial services' for banks.
                    match_str = "financial" if dom_sec == "Banking" else dom_sec.lower()[:4]
                    
                    if stock_sec and dom_sec != "Unknown" and match_str in stock_sec:
                        alpha_score += 20
                else:
                    # US Market lacks dynamic sector rotation here, fallback to fundamental strength
                    margin = yf_t.info.get('profitMargins', 0)
                    if margin and margin > 0.15:
                        alpha_score += 20
            except:
                pass
                
            if alpha_score >= 90 and "ACTION ZONE" in status:
                status = " A+ ASYMMETRIC SETUP"

            
        #  EXEC-01: L2 Tick Data Integration for precise CVD
        l2_df = self.l2_bridge.fetch_us_tick_data(ticker, limit=5000) if market == "US" else self.l2_bridge.fetch_bist_tick_data(ticker)
        if l2_df is not None and not l2_df.empty and len(l2_df) > 2:
            import numpy as np
            tick_cvd = (l2_df['Volume'] * np.sign(l2_df['Price'].diff())).cumsum()
            cvd_val = tick_cvd.iloc[-1]
            # Gradient is the net delta over the entire L2 block (e.g. 5000 ticks), not just the last tick.
            cvd_grad_val = tick_cvd.iloc[-1] - tick_cvd.iloc[0]
        else:
            cvd_series, cvd_grad_series = calculate_cvd(df)
            cvd_val = cvd_series.iloc[-1] if cvd_series is not None and not cvd_series.empty else 0.0
            cvd_grad_val = cvd_grad_series.iloc[-1] if cvd_grad_series is not None and not cvd_grad_series.empty else 0.0
            
        # Normalize CVD Gradient as a percentage of Median Daily Volume
        if mdv20 > 0:
            cvd_grad_val = (cvd_grad_val / mdv20) * 100
        else:
            cvd_grad_val = 0.0

        # The "Liquidity Vacuum" Scanner (Low Float Advantage)
        if market == "BIST" and 0 < mdv20 < 50000000 and cvd_grad_val > 5.0:
            if "ACTION ZONE" in status or "APPROACHING" in status:
                status = f"{status} [LIQUIDITY VACUUM]"
                
        # PROD-03: Gap-Penalty Kelly Adjuster
        gap_penalty_multiplier = 1.0
        try:
            open_prices = df['Open']
            close_prices = df['Close'].shift(1)
            gaps = (abs(open_prices - close_prices) / close_prices).dropna()
            recent_gaps = gaps.tail(50)
            if not recent_gaps.empty:
                avg_gap = float(recent_gaps.mean())
                if avg_gap > 0.005:
                    gap_penalty_multiplier = 1.0 + (avg_gap * 20)
        except:
            pass

        # PROD-05: True Spread (L2) Slippage Proxy
        spread_cost_pct = 0.0
        if 'l2_df' in locals() and l2_df is not None and not l2_df.empty and len(l2_df) > 2:
            import numpy as np
            tick_diffs = l2_df['Price'].diff().abs().replace(0, np.nan).dropna()
            if not tick_diffs.empty:
                avg_spread = float(tick_diffs.mean())
                if current_price > 0:
                    spread_cost_pct = (avg_spread / current_price) * 100
        
        if spread_cost_pct == 0.0:
            # Fallback to daily volatility if L2 tick data is unavailable
            spread_cost_pct = ((df['High'].iloc[-1] - df['Low'].iloc[-1]) / df['Low'].iloc[-1]) * 100
            if pd.isna(spread_cost_pct) or spread_cost_pct < 0:
                spread_cost_pct = 0.0

        # INST-02: Flash-Crash Stink Bidder
        stink_bid = round_to_tick(current_price * 0.85, market)

        # INST-04: US Options IV Ranker (Historical Volatility Proxy)
        options_advice = ""
        if market == "US":
            try:
                import numpy as np
                returns = df['Close'].pct_change().dropna()
                if len(returns) >= 20:
                    hv_20 = returns.rolling(20).std() * np.sqrt(252)
                    hv_lookback = hv_20.tail(252) if len(hv_20) > 252 else hv_20
                    if not hv_lookback.empty:
                        current_hv = hv_lookback.iloc[-1]
                        min_hv = hv_lookback.min()
                        max_hv = hv_lookback.max()
                        if max_hv > min_hv:
                            iv_rank = ((current_hv - min_hv) / (max_hv - min_hv)) * 100
                            if iv_rank < 20:
                                options_advice = "CALL OPTIONS RECOMMENDED (IV Rank < 20%)"
                            elif iv_rank > 80:
                                options_advice = "SHARES ONLY (IV Crush Risk > 80%)"
                            else:
                                options_advice = f"NEUTRAL OPTIONS SPREADS (IV Rank: {int(iv_rank)}%)"
            except:
                pass

        return {
            "ticker": ticker,
            "bucket": bucket,
            "current_price": round(float(current_price), 2),
            "buy_limit": round(float(buy_limit), 2),
            "liquidity_zone_top": round(float(liquidity_zone_top), 2),
            "liquidity_zone_bot": round(float(liquidity_zone_bot), 2),
            "sell_target": round(float(sell_target), 2),
            "stop_loss": round(float(stop_loss), 2),
            "sma_200": round(float(sma200), 2),
            "sma_50": round(float(sma50), 2),
            "atr_14": round(float(atr14), 2),
            "adv_20": round(float(mdv20), 2),
            "max_pos_size": round(float(max_pos_size), 2),
            "cvd": round(float(cvd_val), 2),
            "cvd_gradient": round(float(cvd_grad_val), 2),
            "slippage_risk_pct": round(float(spread_cost_pct), 2),
            "gap_penalty_multiplier": round(float(gap_penalty_multiplier), 2),
            "alpha_score": alpha_score,
            "stink_bid": round(float(stink_bid), 2),
            "options_advice": options_advice,
            "status": status,
            "last_updated": pd.Timestamp.now(timezone.utc).isoformat()
        }
