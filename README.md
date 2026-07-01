# 🛡️ Sovereign Node

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-App-FF4B4B?style=for-the-badge&logo=streamlit)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Supabase-336791?style=for-the-badge&logo=postgresql)
![Quant](https://img.shields.io/badge/Quant-Algorithmic_Trading-000000?style=for-the-badge&logo=python)

A professional-grade, zero-latency trading command center and quantitative engine tailored for Borsa Istanbul (BIST) and US Markets. Designed as a "Bi-Modal" portfolio manager, this system safely balances Core Wealth Protection with Aggressive Momentum Trading.

## 🏗️ System Architecture

The Sovereign Node operates on a strictly decoupled architecture to prevent exchange-side Web Application Firewall (WAF) bans and maintain data sovereignty.

1.  **The Local Sentinel (`src/worker.py`)**: A Python engine that runs on a residential IP. It pulls market data, processes institutional-grade math filters, and pushes limits to the cloud.
2.  **The Vault (Supabase)**: A PostgreSQL cloud database that securely holds the calculated limits, acting as the bridge between your laptop and your mobile device.
3.  **The Command Center (`src/app.py`)**: A Streamlit web application optimized for mobile triage, allowing the operator to view limits, monitor market regimes, and execute safely via their broker.

---

## 💼 Investment Thesis (Funding & Scalability)

This system was built with institutional principles to scale capital efficiently without succumbing to retail trading pitfalls. 

* **Why Fund This Project?** Unlike high-frequency black-box APIs that bleed capital to slippage, this system operates as a Decision Support System ("Bloomberg Panel"). It empowers human execution with institutional-grade risk management.
* **Scalability:** The cloud-native Supabase architecture allows seamless expansion to multi-user SAAS deployments or proprietary firm dashboards.
* **Defensive Edge:** Built-in Regime Filters and ADX Quality Gates protect capital during bear markets, ensuring survivability and long-term compounded growth.

---

## 🧠 Quantitative Logic & Filters

The engine does not just calculate pullbacks; it actively filters out dangerous market conditions.

### Bi-Modal Portfolios
*   **🛡️ THE TANK (Core 70%)**: High-liquidity "Blue Chip" stocks. Entry triggers on an `SMA(20) - 0.5 * ATR(14)` pullback.
*   **🚀 THE SNIPER (Satellite 30%)**: High-volatility growth stocks. Entry triggers on a deeper `SMA(20) - 1.0 * ATR(14)` pullback.

### Institutional Quality Gates
*   **SMA(200) Quality Gate**: (Core Only) Stocks trading below their 200-day Simple Moving Average are automatically rejected to prevent "bottom-fishing" in a downtrend.
*   **Market Regime Filter**: The overall market (BIST-100 / SPY) is measured against its SMA(50). If the macro regime is "BEAR", position sizes are halved in the UI.
*   **ADX Trend Filter**: Stocks with an Average Directional Index (ADX) below 20 are rejected to prevent mean-reversion "shredding" in choppy markets.
*   **1% ADV Market Impact Cap**: Position sizes are capped at 1% of the Average Daily Value (ADV) to ensure orders do not cause spread slippage on illiquid stocks.
*   **USD/TRY Real Alpha Check**: Evaluates if the BIST-100 is yielding a positive real return against the USD/TRY exchange rate.

---

## 🚀 Installation & Setup

### 1. Environment Preparation
Ensure you have Python 3.10+ installed. Install the dependencies:
```bash
pip install -r requirements.txt
```

### 2. Database Initialization
1. Create a free project at [Supabase](https://supabase.com).
2. Go to the SQL Editor and run `geminidocs/schema.sql` to generate the tables.
3. Run `geminidocs/seed_data.sql` to populate your initial CORE and SATELLITE watchlists.

### 3. Environment Variables
Create a `.env` file in the root directory with the following keys from your Supabase Project Settings -> API:
```env
SUPABASE_URL="your-project-url"
SUPABASE_KEY="your-service-role-secret-key"
```

### 4. Running the Node
Run the Local Sentinel (Preferably automated via Windows Task Scheduler at 00:05 TRT):
```bash
python run_worker.py
```

Launch the Mobile Command Center:
```bash
streamlit run src/app.py
```

---

## 📁 Directory Structure

```text
tradepanel/
├── src/
│   ├── app.py           # Streamlit Frontend (Command Center)
│   ├── worker.py        # The Predator Engine orchestrator
│   ├── data_node.py     # Data ingestion & filtering logic
│   ├── db_manager.py    # Supabase connection & JSON sanitization
│   └── indicators.py    # Math: SMA, ATR, ADX, ADV, Tick Rounding
├── geminidocs/
│   ├── schema.sql       # Database table structures
│   ├── seed_data.sql    # Default watchlist tickers
│   └── manual_calc.md   # Emergency manual calculation protocol
├── .env                 # Secret API keys
├── requirements.txt     # Python dependencies
├── operation_plan.md    # Strategic rules and trader protocols
└── README.md            # This documentation
```

---

## ⚖️ Operational Rules (The Sovereign Operator)

1.  **Tick Accuracy**: All limits are pre-rounded to valid Borsa Istanbul tick sizes. Use the "COPY PRICE" button to prevent fat-finger execution errors.
2.  **Conditional Orders**: Bypass human latency by setting Broker Conditional Orders the night before.
3.  **KAP Check Mandatory**: Always verify the Public Disclosure Platform (KAP) before executing an intraday alert. Splits or Dividends invalidate the math.
4.  **No Idle Cash**: Uninvested portfolio capital must be parked in Money Market Funds (PPF) to defend against inflation.
5.  **The Sentinel Rule**: If the Streamlit UI displays a Red "SYSTEM STALE" warning, **DO NOT TRADE**. It means the nightly Python run failed and the limits are expired.
