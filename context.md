# Project Context: Sovereign Node (Portfolio Management Panel)

## 🎯 Terminal Project Goal
This project is **NOT** a high-frequency trading bot designed to compete with hedge funds (that is the purpose of the `AiBotTrader` project in the directory). 

Instead, the **Sovereign Node is a Portfolio Management Panel with built-in risk analyzers and trackers.**
Its primary purpose is to:
1. Analyze a provided watchlist of stocks.
2. Calculate and provide optimal **Buy and Sell Limits**.
3. Identify stocks that have good potential based on technical and risk analysis.
4. Categorize and manage the portfolio into three distinct risk sections.

---

## 🏗️ The 3-Tier Portfolio Structure
The panel organizes the user's portfolio and watchlist into three strict categories based on timeframe and risk profile:

1. **🛡️ THE TANK (Long-Term)**
   - **Purpose:** Long-term investments held for approximately **one year or more**.
   - **Characteristics:** Blue-chip stocks, high liquidity, strong fundamentals. Requires deep pullbacks and strong macro confirmation.

2. **🚀 THE SNIPER (Mid-Term/Potential)**
   - **Purpose:** Stocks with good potential that are worth taking a shot at to profit off them.
   - **Characteristics:** Momentum plays, swing trades, and trend-following setups. Look for aggressive entries and shorter hold times.

3. **🎲 THE GAMBLER (High Risk/Luck)**
   - **Purpose:** Penny stocks, warrants, and high-volatility plays that rely essentially on luck and extreme risk tolerance.
   - **Characteristics:** Highly speculative. The panel provides limits, but acknowledges these are mathematically chaotic and disconnected from institutional safety rules.

---

## 🧬 Current Architecture & State

### 1. The Local Analyzer (`src/worker.py` & `src/data_node.py`)
- **Data Engine**: Fetches market data using `isyatirimhisse` (BIST official data) and `yfinance` (US data).
- **Custom Math (`src/indicators.py`)**: Calculates the technical limits (ATR, SMA, etc.) to generate the Buy/Sell limits without relying on bloated external libraries.

### 2. Risk Analyzers & Trackers
- Calculates Stop-Losses, Breakout Targets, and optimal Entry Limits.
- Features built-in risk constraints like the **1% ADV Cap** (ensuring position sizes do not exceed market liquidity).
- Warns against macro risks (e.g., USD/TRY devaluation vs Nominal Stock Gains).

### 3. The Cloud Vault (`db_manager.py`)
- **Supabase (PostgreSQL)**: Stores the user's `watchlist`, calculated `limits`, and `portfolio` state, allowing the panel to track active positions and historical data.

### 4. The Management Panel (`src/app.py`)
- **Streamlit UI**: The visual dashboard where the user reviews the calculated limits, tracks their open positions across the Tank/Sniper/Gambler tiers, and manages their portfolio risk.

---

## 🤖 AI Handoff Notes (For Future Agentic Developers)
If you are an AI reading this to take over the project:
- **The Bloomberg Panel Paradigm:** We do NOT automate the purchase/execution step. We will never use Alpaca/IBKR execution endpoints or Selenium macros to push trades to a broker. Missing a trade because the user is asleep is mathematically acceptable. We prioritize **Win Size over Win Rate**.
- **The Core Value:** This software is a high-end decision support system. It provides mathematically sound risk calculations, portfolio management, and limit prices. The user will review the UI and execute manually on their own banking app.
- **Next steps**: Refer to `todo.md` for the active roadmap. Focus on enhancing the risk tracking, limit calculations, and the Streamlit UI presentation.
