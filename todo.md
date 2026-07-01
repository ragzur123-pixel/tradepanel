# 📋 Sovereign Node: Portfolio Management Panel Roadmap

> **AI AGENT NOTICE**: The Sovereign Node has evolved into its final form: a **Portfolio Management Panel** divided into Tank, Sniper, and Gambler tiers. The system is structurally complete. The core engine is mathematically immune to Dark Pool volume spoofing, API rate limits, and fundamental hallucination. 

---

## ✅ Phase 1-6: Initial Infrastructure (COMPLETED)
- [x] **Supabase Vault**: Configured with RLS, schemas, and `db_manager.py`.
- [x] **Data Engine**: Uses `isyatirimhisse` and `yfinance`.
- [x] **Custom Math**: Technical indicators implemented in pure Pandas.
- [x] **Command Center UI**: Streamlit dashboard initialized.
- [x] **KAP News Sentinel**: Asynchronous corporate action detection.
- [x] **Sector Rotation**: Sector momentum tracking in the UI.

## ✅ Phase 7-10: The Portfolio Reality Fixes (COMPLETED)
We audited the system through 10 Levels of Reality Checks and implemented the following unassailable fixes:
- [x] **3-Tier Portfolio Restructuring**: UI and logic cleanly separated into **🛡️ THE TANK (1yr+)**, **🚀 THE SNIPER (Potential)**, and **🎲 THE GAMBLER (Luck)**.
- [x] **The Rebalancing Engine**: Drift Calculator built into Streamlit sidebar to enforce 70/30 Tank/Sniper split.
- [x] **Intraday Streaming (cloud_runner.py)**: Shifted from Midnight Cronjobs to 30-minute Intraday Polling to defeat "Rearview Mirror" macro blindness.
- [x] **API Rate-Limit Evasion**: Implemented randomized Jitter and exponential backoff to prevent YF IP bans.
- [x] **Fundamental Protection**: "The Tank" automatically fetches P/E and P/B ratios to veto mathematically bankrupt companies, stopping "Garbage-In, Garbage-Out".
- [x] **Derivative Bypasses**: Bypassed SMA/ATR calculations for "The Gambler" (Warrants/Penny Stocks) to prevent fake math limits.
- [x] **Dark Pool Stripping (MDV)**: Replaced Average Daily Volume with Median Daily Volume (`calculate_mdv`) to ignore institutional block trades and find true retail liquidity.
- [x] **Cloud Migration**: Created `Dockerfile` and `cloud_runner.py` to eliminate local Windows PC single points of failure.
- [x] **Delta-Neutral Stat Arb**: Added `stat_arb.py` pairs-trading scanner to replace premium-bleeding option hedges.

---

## 📋 Sovereign Node x AiTradingBot Integration
**CONTEXT FOR AI AGENT**: Execute these tasks to port the lightweight, deterministic mathematical logic from the terminal AiTradingBot into the Sovereign Node execution panel. The goal is to upgrade the panel's market prediction and risk management without introducing LLM latency or compute costs.

### 🧮 Phase 1: Alpha & Microstructure Pipeline (`src/indicators.py`)
| Task ID | Feature | Action Required | Status |
| :--- | :--- | :--- | :--- |
| ALPHA-01 | Order Flow Integration | Port the Cumulative Volume Delta (CVD) and Aggression Gradients logic into the data pipeline. | [x] |
| ALPHA-02 | Stationary Mean Reversion | Implement Index-Basis Error detection and Ornstein-Uhlenbeck (OU) process stationarity validation using standard Python math libraries. | [x] |
| ALPHA-03 | Liquidity Sweep Detection | Code the Contrarian Trap logic to accurately detect institutional absorption and liquidity sweeps. | [x] |
| ALPHA-04 | Precision Indicator Math | Replace all standard rolling calculations with Wilder's Smoothing (SMMA) for professional-grade RSI and ATR stability. | [x] |

### 🛡️ Phase 2: Risk Desk Hardening (`src/worker.py`)
| Task ID | Feature | Action Required | Status |
| :--- | :--- | :--- | :--- |
| RISK-01 | Intraday Circuit Breakers | Integrate Volatility-Floor Stops to serve as emergency intraday overrides to the existing End-of-Day Stop Logic. | [x] |
| RISK-02 | Multi-Asset Exposure | Implement the Global Risk Overlay to track aggregate vector exposure and enforce currency correlation gates. | [x] |
| RISK-03 | Institutional Drag | Hardcode a 10bps institutional drag into all entry and exit calculations to simulate real-world slippage stress-testing. | [x] |
| RISK-04 | Regime Scaling | Upgrade the binary BEAR regime halving logic to utilize the bot's Dynamic Regime Adaptation formulas for continuous scaling. | [x] |

### 🖥️ Phase 3: Command Center UX (`src/app.py`)
| Task ID | Feature | Action Required | Status |
| :--- | :--- | :--- | :--- |
| UI-01 | CVD Proximity Gauges | Surface the raw Cumulative Volume Delta (CVD) shifts and aggression gradients visually alongside the existing Proximity Gauges. | [x] |
| UI-02 | Global Risk Rebalancer | Feed the new aggregate vector exposure metrics directly into the live visualization of the 70/30 Dynamic Rebalancer. | [x] |
| UI-03 | Gambler Allocation Caps | Build visual alerts for the 5% Gambler allocation that trigger when the OU process flags a pair or index spread at a statistical extreme. | [x] |

### ⚡ Phase 4: Market Microstructure & Execution
| Task ID | Feature | Action Required | Status |
| :--- | :--- | :--- | :--- |
| EXEC-01 | Upgrade Data Ingestion (Level 2) | Transition from 1-minute OHLCV to high-resolution Level 2 order book data for accurate CVD and Contrarian Trap (liquidity sweep) detection. | [x] |
| EXEC-02 | Real-Time Execution (DMA) | Replace static overnight conditionals with real-time webhook executions directly to broker APIs (e.g., IBKR DMA) during live market hours. | [x] |
| EXEC-03 | Local Walk-Forward Optimization | Build rolling WFA into `src/worker.py` (weekend 90-day backtest, 14-day OOS test) to dynamically adjust SMA and ATR multipliers based on regime shifts. | [x] |
| EXEC-04 | Dynamic Slippage Model (TCA) | Replace the flat 10bps drag with a dynamic model tracking historical bid-ask spreads during exact execution windows for true expected profitability. | [x] |

### 📈 Phase 5: Advanced Capital & Execution Physics
| Task ID | Feature | Action Required | Status |
| :--- | :--- | :--- | :--- |
| ADV-01 | Dynamic Position Sizing (Kelly) | Integrate the Half-Kelly formula into `src/worker.py` to dynamically scale capital fraction ($f^*$) per trade based on historical WFA win-rate and profit ratios, replacing static 1% ADV caps. | [x] |
| ADV-02 | Seasonality & Time-Decay | Build an intraday time-matrix ("Lunchtime Veto") and time-decay stops (e.g., 8-hour max) to automatically exit stalled setups and preserve capital velocity. | [x] |
| ADV-03 | BIST-Specific Hedging (Lira Veto) | Expand the Real Alpha Filter to divide BIST closing prices by the daily USD/TRY fixing rate. Veto "Devaluation Mirages" (Nominal highs in TRY but mathematically down in USD). | [x] |
| ADV-04 | Execution Microstructure Dynamics | Upgrade the executor to route Maker (Passive Limit) for Core setups, Taker (Aggressive Limit) for Satellite absorption, and TWAP for low-float BIST tickers nearing capacity. | [x] |

### 🧠 Phase 6: Institutional Alpha Extraction (AiTradingBot Harvest)
| Task ID | Feature | Action Required | Status |
| :--- | :--- | :--- | :--- |
| HARVEST-01 | Statistical Arbitrage Engine | Port `pairs_trading_scanner.py` into the Node to calculate true Beta-neutral Z-Scores for the GAMBLER bucket, finding real-time co-integration breakdowns. | [x] |
| HARVEST-02 | Macro Truth Regime Classifier | Port `regime_classifier.py` to replace static technical indicators with institutional-grade regime detection (Bull/Bear/Choppy) for global risk capping. | [x] |
| HARVEST-03 | Bayesian Self-Auditor | Port `bayesian_self_auditor.py` into the Walk-Forward Optimizer to dynamically throttle the Kelly Criterion based on live mathematical win/loss streaks. | [x] |
| HARVEST-04 | Institutional Sentiment NLP | Upgrade `news_sentinel.py` with the NLP scoring logic from `sentiment_sentinel.py` to provide a true quantified sentiment overlay in the UI cards. | [x] |
| HARVEST-05 | Fundamental Mirage Detector | Port `fundamental_divergence.py` to flag setups where the stock price has fundamentally decoupled from its intrinsic value (earnings/inflation). | [x] |

### 🐺 Phase 7: Deep Alpha Generation (Zero-Cost Expansion)
| Task ID | Feature | Action Required | Status |
| :--- | :--- | :--- | :--- |
| ALPHA-01 | Contrarian Trap Hunter | Port `contrarian_module.py` and `geometry.py`. Identify retail Liquidity Sweeps and institutional Absorption to trade against textbook patterns in the SATELLITE/GAMBLER buckets. | [x] |
| ALPHA-02 | Multi-Timeframe (MTF) Confluence Engine | Upgrade `data_node.py` to calculate technicals across multiple timeframes (1W, 1D, 60m). Only approve entries if macro, primary, and tactical trends are mathematically aligned. | [x] |
| ALPHA-03 | Chief Risk Officer (Active Hedging) | Port `cro_risk.py`. During `BEAR_MOMENTUM` or `CIRCUIT BREAKER` events, automatically select optimal Put Options (US) or Put Warrants (BIST) to generate positive PnL during crashes instead of just sitting in cash. | [x] |

### 🏦 Phase 8: Institutional Capital & Active Trade Management
| Task ID | Feature | Action Required | Status |
| :--- | :--- | :--- | :--- |
| CAP-01 | Dynamic Kelly Position Sizer | Build a global Risk Config in the Streamlit UI to accept `Total Capital` and `Risk %`. Update `app.py` cards to calculate the exact share quantity to purchase based on `(Capital * Risk) / (Entry - Stop Loss)`. | [x] |
| CAP-02 | Active Operations Tab | Create a new Streamlit tab dedicated to tracking OPEN positions. Fetch live prices via `data_node.py` to continuously monitor active trades against dynamic targets. | [x] |
| CAP-03 | Risk-Free Trailing Stops | Implement logic in the Active Operations tab to flag when an asset reaches `Entry + 1 ATR`. Alert the user to move their stop-loss to break-even (Risk-Free Trade) and/or take 50% profit. | [x] |
| CAP-04 | Sector Beta-Stacking Guard | Modify `worker.py` and `app.py` to extract Sector mappings. Reject or flag new signals if the active portfolio already has >2 OPEN trades in the identical sector to prevent high correlation risk. | [x] |
| CAP-05 | Time-Decay Veto (Dead Money) | Add an algorithmic time-tracker. If a logged trade fails to move 1 ATR in the profitable direction within 14 days, flag it as STALE in the UI to free up opportunity cost. | [x] |

### 🛡️ Phase 9: Flawless Execution Protocol
| Task ID | Feature | Action Required | Status |
| :--- | :--- | :--- | :--- |
| EXEC-01 | Pre-Market Gap Trap Detector | Integrate a pre-market data hook in `worker.py`. Veto the setup before open if pre-market trading indicates a gap down past the limit price, preventing instant loss on broker triggers. | [x] |
| EXEC-02 | Live Price Telegram Push | Upgrade `worker.py` webhook to track live tick data and send instant push notifications when a stock crosses the Limit Price or Risk-Free trailing stop. | [x] |
| EXEC-03 | Slippage Auditor | Add an input for `Actual Broker Fill Price` when closing a trade in the UI. Update the Analytics tab to calculate `Theoretical vs. Realized Edge` to track slippage bleed. | [x] |
| EXEC-04 | Macro Blackout Calendar | Fetch economic calendar data. Initiate a "Macro Blackout" to freeze new entries on days with 3-Star macro events (e.g., CPI, FOMC) to prevent volatility gambling. | [x] |
| EXEC-05 | Tail-Risk CRO UI | Implement a UI module that activates during `BEAR` regimes, displaying the optimal hedge (e.g., SQQQ, XU030 Put Warrants) as calculated by `cro_risk.py`. | [x] |

### 🚀 Phase 10: The Alpha Synthesizer
| Task ID | Feature | Action Required | Status |
| :--- | :--- | :--- | :--- |
| ALPH-01 | A+ Conviction Scoring & Kelly Multiplier | Build an "Alpha Score" (0-100) using ADX, Volume, Sector, and NLP. If score > 90, flash "A+ ASYMMETRIC SETUP" in the UI and automatically multiply the Kelly Position Sizer. | [x] |
| ALPH-02 | Multi-Timeframe Fractal Alignment | Upgrade `data_node.py` to check `1wk` charts. Reject setups if the daily trend is bullish but the macro weekly trend is bearish to prevent false breakouts. | [x] |
| ALPH-03 | Institutional Volume Node (VWAP) | Integrate intraday/daily VWAP. If the Buy Limit doesn't align with a high-volume institutional support node, adjust it down to the nearest volume shelf. | [x] |
| ALPH-04 | Psychological Tilt Lockout | Track consecutive stop-outs in the database. If 3 consecutive losses hit in 24 hours, initiate a UI `TILT LOCKOUT` blurring new signals to prevent revenge trading. | [x] |
| ALPH-05 | Earnings IV-Crush Veto | Cross-reference Yahoo Finance earnings calendar. If a stock is within 3 days of an earnings report, flag it with `VETO: EARNINGS IV-CRUSH RISK`. | [x] |

### 🏛️ Phase 11: The Institutional Edge
| Task ID | Feature | Action Required | Status |
| :--- | :--- | :--- | :--- |
| INST-01 | Real-Yield PnL Auditor | Add a "Real Yield" toggle in Analytics tab. Fetch historical USD/TRY exchange rates to calculate true Net USD PnL for BIST trades, exposing inflation decay. | [x] |
| INST-02 | Flash-Crash Stink Bidder | Generate a secondary limit price (-15% from current price) at extreme structural support for providing liquidity during algorithmic flash crashes. | [x] |
| INST-03 | Automated Morning Briefing | Build an export module (Markdown/PDF) that summarizes Macro Regime, top 3 "A+" limits, and active trailing stops for a 2-minute daily prep routine. | [x] |
| INST-04 | US Options IV Ranker | Calculate Implied Volatility Rank for US setups. If IV < 20%, advise Call Options. If IV > 80%, advise Shares only to avoid Vega decay. | [x] |
| INST-05 | Pair-Trading Divergence Scanner | Scan highly correlated asset pairs. Flash a "PAIRS ARB" setup when spread diverges by >2 standard deviations. | [x] |

### 🛑 Phase 12: Production Hardening & Capital Safety
| Task ID | Feature | Action Required | Status |
| :--- | :--- | :--- | :--- |
| PROD-01 | Broker Truth-Sync UI | Create a reconciliation interface where the user inputs exact physical broker holdings daily to correct AI "Ghost Positions" and detachments. | [x] |
| PROD-02 | Corporate Action Suppressor | Query dividend/split calendars to actively suppress false technical breakdown signals and prevent incorrect stop-loss triggers on ex-div dates. | [x] |
| PROD-03 | Gap-Penalty Kelly Adjuster | Calculate historical overnight gap probabilities. Artificially expand the Kelly risk denominator for gap-prone assets to prevent max-drawdown violations. | [x] |
| PROD-04 | Dual-Oracle Data Redundancy | Implement a secondary API validation check for price anomalies. If `yfinance` reports a >15% daily drop, suspend limits until verified to prevent split-crush buys. | [x] |
| PROD-05 | True Spread (L2) Slippage Proxy | Replace the naive `(High-Low)/Low` volatility proxy with actual L2 Bid-Ask spread data (via `fetch_bist_tick_data`) for mathematically sound transaction cost calculation. | [x] |

### ⚙️ Phase 13: Operational Infrastructure
| Task ID | Feature | Action Required | Status |
| :--- | :--- | :--- | :--- |
| OPR-01 | BIST Tick Size Matrix | Update `round_to_tick()` to mathematically comply with all Borsa Istanbul dynamic price brackets (up to 2500+ TL) to prevent sub-penny execution rejections by brokers. | [x] |
| OPR-02 | Settled Cash Sizer Constraint | Constrain the Kelly position sizing algorithm so `exposure <= settled_cash` to prevent overleveraging and margin wall hits. | [x] |
| OPR-03 | Retroactive Portfolio Split Adjuster | Build logic to retroactively scan and adjust `entry_price` and `qty` of open portfolio database positions when a split occurs to prevent ghost -50% stop-loss triggers. | [x] |
| OPR-04 | Local SQLite Cache Buffer | Implement a local SQLite layer for UI reads to decouple `app.py` from Supabase REST rate limits, preventing death loops and UI lockouts during extreme volatility. | [x] |
| OPR-05 | Human Execution Drag Warning | Add a UI indicator that flags high CVD / L2 setups as "Tick Sensitive", explicitly warning the user that manual execution latency will severely degrade the calculated alpha. | [x] |

### 🚨 Phase 14: The Execution Reality Patch
| Task ID | Feature | Action Required | Status |
| :--- | :--- | :--- | :--- |
| EXE-01 | Independent Portfolio Pricing Engine | Decouple portfolio live pricing from the setup screener. Force `app.py` or `worker.py` to fetch real-time quotes for all open positions to prevent PnL flatlining (0.00% blind spots). | [x] |
| EXE-02 | Partial-Exit Analytics Integrity | Build a "Scale Out / Partial Close" function in the UI. Log partial realized PnL explicitly while keeping the remainder of the position `OPEN`, preserving Bayesian edge analytics. | [x] |
| EXE-03 | Silent Death Supervisor | Build an explicit UI 'Data Freshness' heartbeat tracker that triggers a visual alarm if `worker.py` fails to complete a cycle in the last 15 minutes, preventing blind trading on stale limits. | [x] |
| EXE-04 | Market State Machine (EoD Desync) | Implement logic to differentiate between Live Market, Pre-Market, and Settlement. Prevent `worker.py` from generating limits off fractured or delayed `1d` candles during the 18:00 - 18:20 closing transition. | [x] |

### 🛡️ Phase 15: The Execution Discipline Patch
| Task ID | Feature | Action Required | Status |
| :--- | :--- | :--- | :--- |
| DIS-01 | Slippage Audit (The "Perfect Fill" Fix) | Destroy the assumption that users fill at exact `buy_limit` prices. Modify `app.py` setup cards to mandate manual input of `Actual Fill Price` and `Actual Fill Qty` before allowing a trade log. | [x] |
| DIS-02 | Hard GTC Stop Mandate | Embed an explicit, un-ignorable UI directive on setup cards instructing the user to "PLACE GTC STOP LIMIT AT BROKER IMMEDIATELY." The panel is not a stop-loss engine; the physical broker is. | [x] |
| DIS-03 | Sector Beta-Stacking Veto | Evolve the passive sector logger into an active constraint. Force `worker.py` to veto any new setup if the portfolio already holds an `OPEN` position in that exact sector, preventing systemic contagion. | [x] |

### 🔄 Phase 16: State Synchronization & Garbage Collection
| Task ID | Feature | Action Required | Status |
| :--- | :--- | :--- | :--- |
| SYNC-01 | Ghost Limits Garbage Collector | Modify `db_manager.py` to aggressively purge old limit calculations for any ticker that has been removed from the `watchlist_full` table, preventing stale alpha poisoning. | [x] |
| SYNC-02 | UI Position Modifier (Trail Stop) | Add UI inputs in the Active Operations tab allowing users to surgically update `stop_loss` and `exit_target` for `OPEN` positions, ensuring the DB state mirrors broker reality (e.g., trailing stops to break-even). | [x] |
| SYNC-03 | Liquidity Lock Kelly Cap | Implement a hard-cap override on the Kelly Sizer (e.g., Max Exposure cannot exceed 15% of `capital`), defending the portfolio against single-asset circuit-breaker locks where theoretical stops fail. | [x] |

### 💼 Phase 17: The Portfolio Reality Check
| Task ID | Feature | Action Required | Status |
| :--- | :--- | :--- | :--- |
| PRTF-01 | Global Margin Manager | Modify `app.py` to dynamically sum the total capital locked in `OPEN` positions and deduct it from `Total Capital`. Force Kelly Sizer to size solely on true `Available Settled Cash` to prevent margin overextension. | [x] |
| PRTF-02 | Retroactive Dividend Adjuster | Expand `worker.py`'s split adjuster to monitor for Dividends. Automatically deduct the gross dividend amount from the `entry_price`, `stop_loss`, and `exit_target` of `OPEN` positions to prevent phantom stop-outs. | [x] |

### 🧮 Phase 18: The Structural Math Audit
| Task ID | Feature | Action Required | Status |
| :--- | :--- | :--- | :--- |
| EXEC-05 | FX Normalized Kelly Sizer | Modify `app.py` to correctly apply the live USD/TRY exchange rate to the `settled_cash` and `active_exposure` limits for US equities, preventing a 35x margin over-leverage when mixing TRY risk parameters with USD asset prices. | [x] |
| EXEC-06 | Anti-Pyramiding Database Lock | Modify `app.py` to proactively read the `ALREADY LONG` status and physically disable the `LOG TRADE` UI button for duplicate tickers, preventing users from ignoring the AI and averaging down into losing positions. | [x] |

### 💱 Phase 19: Dual-Currency Margin Isolation
| Task ID | Feature | Action Required | Status |
| :--- | :--- | :--- | :--- |
| PRTF-03 | Dual-Currency Cash Silos | Hard-fork the Global Margin Manager in `app.py` into two isolated cash pools (`TRY` and `USD`). Stop cross-subtracting US exposure from BIST capital. Ensure Kelly Sizer routes `settled_cash` limits to the exact native currency of the asset. | [x] |

### 🧠 Phase 20: Persistent Execution Environment
| Task ID | Feature | Action Required | Status |
| :--- | :--- | :--- | :--- |
| EXEC-07 | Ephemeral Capital Trap | Connect the UI risk inputs (`capital_try`, `capital_usd`, `risk_pct`) directly to the Supabase `metadata` table. Ensure these parameters are fetched on launch and persisted on every change so the Kelly Math Engine doesn't default to lethal dummy sizes upon browser refresh. | [x] |

### 💣 Phase 21: The Bayesian Time Bomb
| Task ID | Feature | Action Required | Status |
| :--- | :--- | :--- | :--- |
| PRTF-04 | Defuse Tilt Lockout | Fix the dictionary key mismatch in `bayesian_self_auditor.py`. Change `"pnl"` to `"net_pnl"` and add a fallback logic check `exit_price > entry_price` to prevent the auditor from assuming a 100% loss rate and permanently bricking the execution panel after 50 trades. | [x] |

### 🗑️ Phase 22: The Database Purge Anomaly
| Task ID | Feature | Action Required | Status |
| :--- | :--- | :--- | :--- |
| SYNC-04 | Watchlist Garbage Collector Repair | Rewrite the Ghost Limits Garbage Collector in `db_manager.py`. Stop comparing database limits against the `worker.py` execution loop outputs (which skip tickers during settlement/timeouts). Cross-reference directly with the `watchlist` database table to definitively identify true orphaned setups. | [x] |

### 🧟 Phase 23: The Zombie Position Paralysis
| Task ID | Feature | Action Required | Status |
| :--- | :--- | :--- | :--- |
| SYNC-05 | Truth-Sync Zombie Purge | Update the `PROD-01: State Truth-Sync UI` in `app.py`. If a user manually overrides a position's `qty` to `0`, physically overwrite the database `status` to `"CLOSED"` to prevent immortal 0-quantity trades from permanently consuming the 5-slot portfolio capacity and locking tickers out of future setups. | [x] |

### ⚠️ Phase 24: The OCO Cancellation Trap
| Task ID | Feature | Action Required | Status |
| :--- | :--- | :--- | :--- |
| EXEC-08 | OCO Naked Short Warning | Inject a hard alert into the "Execute Exit" UI component in `app.py`. Ensure the user is physically reminded to manually cancel their resting GTC Stop Loss and Target orders at the broker immediately after logging an exit to prevent catastrophic accidental naked shorting upon a V-shape reversal. | [x] |

### 🛑 Phase 25: The Revenge Trading Loop
| Task ID | Feature | Action Required | Status |
| :--- | :--- | :--- | :--- |
| DIS-04 | 24-Hour Cool-Down Veto | Inject a state-aware cool-down mechanism into `worker.py`. Query the `portfolio` table for trades closed at a loss (`net_pnl < 0`) within the last 24 hours. Override the status of any matching ticker to `"24H COOL-DOWN"` to physically lock the UI and prevent algorithmic revenge-trading of falling knives. | [x] |

### 🕵️ Phase 26: Forensic Workflow & Logic Patches
| Task ID | Feature | Action Required | Status |
| :--- | :--- | :--- | :--- |
| PRED-01 | KAP Chronological Fix | Update `operation_plan.md` and `USER_MANUAL.md` to invert the morning sequence: Audit KAP disclosures at 08:40 AM strictly *before* opening the Streamlit dashboard at 08:45 AM. | [x] |
| PRED-02 | The Sector Gate | Program logic into `run_worker.py` that prevents the dashboard from recommending more than two tickers from the same BIST sector simultaneously. | [x] |
| PRED-03 | PPF Liquidity Math | Configure `src/app.py` to calculate the exact TRY value required from Money Market Funds (PPF) alongside generated limit prices to clear the 09:00 AM triage bottleneck. | [x] |
| PRED-04 | Midnight Hazard Check | Enhance the stale-check logic to catch upstream scraper failures (e.g., weekend bypasses), ensuring the dashboard locks if BIST data didn't fully settle. | [x] |
| PRED-05 | BIST Circuit Breaker Override | Upgrade stop-loss mechanisms to override the EOD-only rule in BIST markets (triggering exits if price hits -5% or -7% limits) to avoid limit-down (-10%) illiquidity traps. | [x] |
| PRED-06 | Tank Volatility Realignment | Adjust the `SMA_20 - (0.5 * ATR_14)` Tank pullback to a deeper threshold (or dynamic scale) to prevent buying micro-downtrend midpoints in BIST-30 assets. | [x] |
| PRED-07 | ADX Momentum Calibration | Adjust the static `ADX > 20` threshold to ensure it identifies trend inception rather than exhaustion for aggressive BIST growth equities. | [x] |
| PRED-08 | Global Equity Cap | Implement a new Risk Config constraint ensuring no single position exceeds a predefined maximum percentage of total account equity (e.g., max 10%), augmenting the 1% ADV limit. | [x] |

### 🔬 Phase 27: The Micro-Fractures (Second-Order Edge Cases)
| Task ID | Feature | Action Required | Status |
| :--- | :--- | :--- | :--- |
| MICRO-01 | BIST Tick-Size Rejection Trap | Implement custom BIST tick-rounding function (Adım Kuralı) in `worker.py` to round limits (0.01 for <20 TRY, 0.02 for 20-50, 0.05 for 50-100, 0.10 for >100) to prevent broker rejection. | [x] |
| MICRO-02 | PPF Settlement Illusion | Update `system_manifest.md` to whitelist T+0 PPFs only (e.g., RPD, TI1, ICZ) or enforce a static 5% Tactical Cash Buffer to prevent T+1 settlement lockouts during 10:00 AM fills. | [x] |
| MICRO-03 | Macro Regime Whipsaw | Implement Schmitt Trigger (Hysteresis) logic for the macro regime filter to prevent high portfolio turnover. Use a ±1.5% buffer band around the SMA50 instead of a binary cross. | [x] |
| MICRO-04 | Historical Data Corruption | Build a Price Deviation Gate in `data_node.py` that aborts updates if `(Close_Today / Close_Yesterday) < 0.60`, preventing the math engine from hallucinating false limits due to unprocessed splits. | [x] |
| MICRO-05 | Partial Fill Orphan Problem | Implement a Time-Decay Fill Rule in the daily protocol. Audit orders at 12:30 PM TRT: cancel resting portions <35% filled, or liquidate dust positions <15% filled to prevent trailing orphaned fragments. | [x] |
| MICRO-06 | Sığ Hisse Volume Trap | Upgrade Quant Gate 4 to use a dual-metric cap: `Min(0.01 * ADV, 0.0005 * (Market Cap * Free Float %))` to protect against spoofed telegram pump volumes in low free-float equities. | [x] |
| MICRO-07 | Database UPSERT Composite Key | Audit the `db_manager.py` schema and push logic. Ensure `worker.py` performs an `UPSERT` using a composite primary key (`ticker`, `run_date`) to prevent duplicate limit spam and accidental retrieval of old limits. | [x] |

### 🚨 Phase 28: Production Readiness & Security Fixes
| Task ID | Feature | Action Required | Status |
| :--- | :--- | :--- | :--- |
| PROD-SEC-01 | Streamlit Authentication Gate | Implement a session-state password gate in `app.py` to prevent unauthorized public access to the financial database and override functions. | [x] |
| PROD-SEC-02 | GTC Gap Execution Veto | Update `operation_plan.md` to deprecate blind GTC night-before entries. Enforce manual 09:40 AM limit verification to prevent executing into gap-down traps. | [x] |
| PROD-SEC-03 | Run-Date Fetch Integrity | Update `get_limits()` in `app.py` to filter `supabase.table("limits")` by the current `run_date` to prevent duplicate limit cards from flooding the UI. | [x] |
| PROD-SEC-04 | Asynchronous Data Ingestion | Wrap data fetching in `worker.py` with `concurrent.futures.ThreadPoolExecutor` to eliminate synchronous timeouts and ensure the 100+ ticker pipeline completes before the settlement deadline. | [x] |

### 💥 Phase 29: Systemic Execution Failures
| Task ID | Feature | Action Required | Status |
| :--- | :--- | :--- | :--- |
| EXEC-FAIL-01 | Stop-Loss Contradiction | Align the Streamlit UI with the EOD-only math engine. Remove the "PLACE GTC STOP LIMIT" warning in `app.py` and replace it with an EOD mental stop protocol directive. | [x] |
| EXEC-FAIL-02 | Database Schema Rejection | Update `geminidocs/schema.sql` to include `stink_bid`, `cvd`, `cvd_gradient`, `gap_penalty_multiplier`, `alpha_score`, and `options_advice` to prevent HTTP 400 rejection during payload upserts. | [x] |
| EXEC-FAIL-03 | Intraday Double-Dipping Glitch | Update `app.py` to dynamically cross-reference the open portfolio at render time and hide the `LOG TRADE` button if the ticker is already open, preventing duplicate manual entries. | [x] |

### 🛑 Phase 30: The Bloomberg Panel Enforcement
| Task ID | Feature | Action Required | Status |
| :--- | :--- | :--- | :--- |
| EXEC-FAIL-04 | Rogue DMA Engine Neutralization | Remove `BrokerDMA` integration from `worker.py` to prevent unauthorized automated execution. Hardcoded mock capital (`100,000` for both USD and TRY) would lead to catastrophic real-world position sizing. The panel must remain a pure Decision Support System. | [x] |
| EXEC-FAIL-05 | Phantom Cash Trap (Margin Breach) | Re-route `settled_cash` logic inside `app.py` `render_single_card` to subtract actual live portfolio exposure (`active_try`/`active_usd`) from total capital. The previous logic wrongly assumed 100% of the portfolio was always liquid, sizing trades into margin calls. | [x] |
| EXEC-FAIL-06 | Unexecutable Limits (Circuit Breaker Reject) | Update BIST Circuit Breaker logic in `data_node.py` to constrain Stop-Loss and Buy Limit against the *actual* Exchange Limit Down (`prev_price * 0.905`), not the calculated entry price. Prevents brokers rejecting unexecutable limit orders. | [x] |
| EXEC-FAIL-07 | Orphaned Portfolio Risk Trap | Update `worker.py` and `db_manager.py` to inject `open_positions` into the data ingestion loop, and prevent `SYNC-01` from garbage collecting them. Previously, removing a ticker from the Watchlist would completely blind the panel to live risk management (Stop Loss / TP) for that ticker. | [x] |
| EXEC-FAIL-08 | Stock Split Stop-Loss Trap | Update `OPR-03` split adjustment logic in `worker.py` to correctly scale `stop_loss` and `exit_target` alongside `entry_price`. Previously, a 2:1 split would halve the current price but leave the stop loss at its original unadjusted height, instantly triggering an artificial "Stop Loss Hit" Telegram alert and forcing the user out of a healthy position. | [x] |
| EXEC-FAIL-09 | Settlement Window Blackout Trap | Remove `bist_settlement_active` blocker in `worker.py`. The panel previously aborted all data ingestion and Telegram alerts between 18:00 and 18:20 (BIST closing auction). Since the user relies on EOD mental stops at the exact market close, this blackout literally blinded them at the critical moment of execution, forcing them to hold losing positions overnight into gap-down traps. | [x] |
| EXEC-FAIL-10 | Stale Limits Database Sorting Trap | Update `get_limits()` in `app.py` to use `.order('run_date', desc=True)` and deduplicate by ticker. Previously, PostgreSQL's unordered queries could return historical limits last, randomly overriding the UI with Buy Limits and Stop Losses from previous days. This would cause the user to input structurally incorrect orders into their broker. | [x] |
| EXEC-FAIL-11 | Circuit Breaker Kelly Over-Leverage Trap | Remove logic in `data_node.py` that forced `dynamic_stop = exchange_limit_down`. By artificially pulling the true structural stop loss UP to the daily Exchange Limit Down, the `risk_gap` was artificially narrowed. This caused the Kelly Sizer to recommend massive, over-leveraged position sizes that would lead to catastrophic drawdowns when the true structural stop was eventually hit on subsequent days. | [x] |
| EXEC-FAIL-12 | The Phantom Take-Profit Trap | Added `exit_target` checking logic to the Telegram Alert loop in `worker.py`. Previously, the panel would alert the user when their stop loss was hit or when to move their stop to breakeven, but would LITERALLY NEVER alert the user when their ultimate Take Profit was reached. The user would blindly hold winning trades until they reversed and stopped out at breakeven, resulting in a 0% real-world win rate. | [x] |
| EXEC-FAIL-13 | Unadjusted Corporate Action Data Poisoning | Tightened the `MICRO-04` Historical Data Corruption gate in `data_node.py`. It was previously set to abort if a stock dropped >40% overnight. However, BIST has a strict 10% daily limit down. This meant that unadjusted dividends or minor splits causing a 12% to 39% drop were allowed through, completely poisoning the ATR and moving averages and generating wildly false signals. The gate now rigorously rejects any BIST drop >12%. | [x] |
| EXEC-FAIL-14 | Database Infinity Poisoning | Updated `push_limits` in `db_manager.py` to sanitize `np.inf` and `-np.inf`. Previously, if a single halted stock generated a division-by-zero (e.g., in ADX calculation), the resulting Infinity value would cause PostgreSQL's JSONB constraint to reject the entire batch of calculated limits with a 400 Bad Request. This would silently freeze the entire panel on stale limits for the day. | [x] |
| EXEC-FAIL-15 | Streamlit Suggested Shares UI Crash | Updated `app.py` logging inputs to use `max(1, int(suggested_shares))`. Previously, if a trade was generated but the user had no settled cash, `suggested_shares` fell to 0. Since Streamlit's `st.number_input` requires `value >= min_value` (1), passing 0 caused a fatal `StreamlitAPIException` that crashed the entire UI, completely blinding the user to all other trading opportunities. | [x] |
| EXEC-FAIL-16 | Corporate Action Entry-Date Corruption Trap | Updated `OPR-03` and `PRTF-02` in `worker.py` to track corporate actions via the `notes` column instead of overwriting the `entry_date`. Previously, whenever a stock split or paid a dividend, the system reset the `entry_date` to `now()` to prevent double-counting. This permanently destroyed the trade's actual hold-time, entirely bypassing the 14-day `CAP-05` Time-Decay stop-loss mechanism and trapping capital in dead-money positions. | [x] |
| EXEC-FAIL-17 | The Google Finance Veto Trap | Updated `PROD-04` Dual-Oracle Data Redundancy in `data_node.py`. When a stock moved >15% in a single day, the system attempted to cross-reference the price with Google Finance via a naive web scraper. If the scrape failed due to a CAPTCHA, 403 rate-limit, or HTML layout change, it defaulted to `is_data_poisoned = True`, automatically vetoing the trade. This catastrophically blocked the panel from trading highly profitable breakout momentum stocks. | [x] |
| EXEC-FAIL-18 | Corporate Action Split Date Exception | Fixed a `NameError` in `worker.py`. During a stock split adjustment, `split_date` was referenced in the execution logic but was never defined. If a split occurred, this unhandled exception would crash the entire worker thread before it could push limits to the panel. | [x] |
| EXEC-FAIL-19 | UnboundLocalError in Sector Alpha Bonus | Fixed an `UnboundLocalError` in `data_node.py`. `yf_t` was instantiated conditionally inside the `ALPH-02` block (only if `"ACTION ZONE"` was triggered). Later, the institutional alpha scorer checked `yf_t.info` regardless of the status. If the stock was only `"APPROACHING"`, `yf_t` was undefined, throwing a silent exception that bypassed the entire alpha scoring mechanism and prevented A+ setups from receiving their alpha bonus. | [x] |
| EXEC-FAIL-20 | Bayesian Bucket Contamination on Partial Exits | Fixed partial exit logic in `app.py`. When manually executing a partial exit, the system inserted a new `CLOSED` trade to record the realized PnL but failed to carry over the `bucket` metadata. This meant highly volatile `GAMBLER` partial exits defaulted to `CORE`, irreversibly corrupting the `BayesianSelfAuditor`'s win-rate tracking and causing the Kelly Criterion to heavily mis-size future `CORE` trades. | [x] |
| EXEC-FAIL-21 | ZeroDivisionError in OU Mean Reversion | Fixed a `ZeroDivisionError` in `indicators.py`. In `calculate_ou_params()`, if a pair perfectly correlated forming a pure random walk, `beta` could equal `1.0`. Calculating `mu = alpha / (1 - beta)` would crash the Pairs Arbitrage scanner. Added a constraint to default to `series.mean()` if `beta` equals 1.0. | [x] |
| EXEC-FAIL-22 | Volatility Floor Stop NaN Propagation | Fixed a `NaN` propagation risk in `data_node.py`. When calculating `v_floor` (intraday circuit breaker stops) via a 20-day standard deviation, any stock with less than 20 days of data returned `NaN`. `max(atr14, NaN)` in Python inherently evaluates to `NaN` depending on argument order, resulting in `NaN` stop losses being pushed to the database, breaking JSONB formatting and panel display. | [x] |
| EXEC-FAIL-23 | False Positive Error State on Empty Watchlist | Fixed a UI heartbeat synchronization bug in `worker.py`. If the market was highly bearish and the Risk Gates successfully rejected all trades, the worker reported `status="ERROR"`. This caused the entire panel to flash a system failure state simply because it was protecting capital. Updated to report `status="OK"` with `0 Limits Active`. | [x] |
| EXEC-FAIL-24 | Supabase Schema Concurrency Wipe | Fixed a race condition where `app.py` and `worker.py` were using `.upsert()` on the `metadata` table, repeatedly wiping each other's configuration data out (worker deleted UI capital inputs, UI deleted worker market regime status). Replaced with precise `.update().eq("id", 1)` calls. | [x] |
| EXEC-FAIL-25 | Undefined Columns in Database Migration | Fixed `schema.sql` missing `capital_try`, `capital_usd`, `risk_pct`, `liquidity_zone_top`, and `liquidity_zone_bot`. These columns were referenced natively by `app.py` and `data_node.py` but absent in the DDL, which would have instantly crashed both the UI and the Data Pipeline upon attempting to execute API insertions. | [x] |
| EXEC-FAIL-26 | Sidebar Configuration CSS Lockout | Removed a CSS rule `[data-testid="stSidebar"] { display: none !important; }` in `app.py` that permanently hid the Streamlit sidebar, locking users out of modifying their "Institutional Capital" and "Risk Percentage" settings. | [x] |
| EXEC-FAIL-27 | Supabase Column Name Mismatch (Crash) | Fixed a catastrophic querying bug in `app.py` where it attempted to `.order('created_at', desc=True)` on the `portfolio` table. The column `created_at` does not exist in the schema, causing the Trade Journal and Slippage Auditor to fail fetching closed trades. Changed to `exit_date`. | [x] |
| EXEC-FAIL-28 | Limit Table Exponential Bloat | Added a PRG-01 Auto-Purge step to `db_manager.py` that deletes rows in the `limits` table where `run_date` is older than 7 days. Without this, the table grew by exactly 1 row per ticker per day, destroying database API speed. | [x] |
| EXEC-FAIL-29 | Naked PnL Friction Bleed | Updated the `app.py` exit logic to automatically deduct a strict 0.3% round-trip friction cost from `net_pnl`. Previously, it calculated pure gross PnL, creating a massive discrepancy against the true alpha reality of live manual execution. | [x] |
| EXEC-FAIL-30 | Bayesian Auditor Win-Rate Flaw | Fixed `bayesian_self_auditor.py` to strictly evaluate a "Win" as `net_pnl > 0`. The previous logic had a secondary bypass `or exit_price > entry_price` which allowed slightly unprofitable trades (due to 0.3% slippage) to be falsely recorded as a "Win", tricking the Kelly Criterion engine into over-leveraging on false confidence. | [x] |
| EXEC-FAIL-31 | Alpha Score RVOL Intraday Handicap | Fixed `data_node.py` to prorate `today_vol` based on elapsed trading hours before calculating RVOL. Because yfinance daily data gives partial volume intraday, `RVOL > 1.5` was mathematically impossible to trigger until 3:59 PM. The Alpha engine is now freed to flag `A+` breakouts early in the session. | [x] |
| EXEC-FAIL-32 | Missing ADX_14 Alpha Logic | Injected `calculate_adx` directly into `run_alpha_pipeline`. The scoring algorithm explicitly checked `if 'ADX_14' in df.columns` to award 15 points for trend strength, but the dataframe never actually generated the column, permanently suppressing the Kelly Confidence Score for all setups. | [x] |
| EXEC-FAIL-33 | Institutional Absorption Polarity Flaw | Corrected `geometry.py`'s `detect_absorption()` logic. It previously categorized negative delta with small candle bodies (heavy retail selling met by limit buys) as "Bearish Absorption", when mathematically this is Institutional Accumulation (Bullish). This completely broke the worker's PRED-03 Reversal Filter. | [x] |
| EXEC-FAIL-34 | The False Kelly Formula Destruction | Rewrote the Kelly Criterion in `app.py`. The formula was catastrophically coded as `(p - q) / b` instead of `p - (q / b)`. This mathematical error mathematically evaluated to 0 for highly profitable setups (e.g. 1:3 R/R), locking the user out of the most asymmetric trades. | [x] |
| EXEC-FAIL-35 | Kelly Sizer UI Disconnect | Fully wired `BayesianSelfAuditor` into `render_single_card`. Previously, the True Kelly win-rates were shown on Tab 4 but ignored in the actual limit card sizing, which just used a static 1.0% fraction. The limit cards now actively shrink risk exposure during losing streaks and output a "KELLY VETO" badge if edge < 0. | [x] |
| EXEC-FAIL-36 | Lost Regime Risk Overlay | Restored Macro Regime Target Scaling to `data_node.py`. When `worker.py` execution blocks were purged, the logic that shrinks targets by 30% in Bear Rallies was lost, completely destroying R/R expectancy in crashes. | [x] |
| EXEC-FAIL-37 | The Mirage Veto Intraday Data Leak | Updated `vol_z` calculation in `data_node.py` to use `today_vol_projected`. Using un-prorated `today_vol` caused volume z-scores to artificially plummet to -2.0 at the market open, falsely triggering the `HARVEST-05 MIRAGE DETECTED` veto and banning the strongest momentum stocks. | [x] |
| EXEC-FAIL-38 | Missing Entry Date Database Hole | Updated `app.py` manual trade logging to insert `entry_date`. Without this, the `CAP-05` Time-Decay Dead Money Veto failed silently, trapping user capital in dead trades for months because the `days_in_trade` logic received `None`. | [x] |
| EXEC-FAIL-39 | Sector Alpha UnboundLocalError | Fixed a silent failure in `data_node.py` where `yf_t` was instantiated conditionally, causing setups in the `APPROACHING` state to hit an `UnboundLocalError` and completely bypass the 20-point Sector Momentum alpha bonus. | [x] |
| EXEC-FAIL-40 | Yahoo Finance Sector String Mismatch | Fixed `data_node.py` Sector Bonus logic. The system evaluated `Banking` against Yahoo's `Financial Services`, guaranteeing that no BIST bank ever received sector momentum credit. Cross-contamination between US equities and BIST sector strength was also isolated. | [x] |
| EXEC-FAIL-41 | L2 Tick-Data CVD Gradient Wipeout | Updated `cvd_grad_val` logic. The system was applying `.diff().iloc[-1]` to high-res Tick Data, which mathematically extracted the volume of a *single trade* (e.g., 5 shares) instead of the session's cumulative momentum block, driving the UI CVD gauge to a flat 0.0%. | [x] |
| EXEC-FAIL-42 | BIST Core Portfolio ADX Lockout | Fixed a massive flaw in `worker.py` where BIST CORE setups were being vetted using the `bist_adx` (the BIST-100 Index ADX) instead of the individual stock's `ticker_adx`. Because indices rarely sustain ADX > 20, the system was permanently banning almost all BIST Core trades regardless of the stock's actual trend strength. | [x] |
