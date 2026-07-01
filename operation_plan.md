# Operation: Sovereign Node Blueprint (Aggressive Predator Edition)

## 🎯 Strategic Objective
Build a professional-grade, zero-latency trading command center with a dual-tier portfolio designed to capture real (USD-adjusted) returns while neutralizing market-impact and choppy-regime risks.

---

## 🏗️ Phase 1: The Cloud Foundation (Database)
We use **Supabase** (PostgreSQL) as our single source of truth.
1.  **Schema Execution**: Run `geminidocs/schema.sql`.
2.  **The Pre-Run Wake-Up**: The Local Worker pings Supabase at 23:55 TRT.

## 🛰️ Phase 2: The Local Sentinel (Data Worker)
**Predatory Fail-Safe Protocol**: The Home Node is the engine.
1.  **The Aggressive Math Filters**:
    *   **ADX Trend Filter**: Only stocks with **ADX(14) > 20** are processed. This ensures the market is "Trending" and avoids being "shredded" in choppy ranges.
    *   **USD/TRY Real-Return Filter**: The worker checks if BIST-100 returns exceed USD/TRY devaluation. If not, signals are flagged as "Negative Real Alpha."
    *   **1% ADV Limit**: The worker calculates a maximum position size for every signal, capped at **1% of the Average Daily Value (ADV)**. This ensures your own orders do not move the market against you.
2.  **CORE (70%)**: SMA(200) + SMA(50) + 0.5 ATR.
3.  **SATELLITE (30%)**: SMA(20) + 1.0 ATR + Spread Filter (<0.5%).

## 📱 Phase 3: The Mobile Command (Streamlit UI)
1.  **Regime Health**: Displays "Market Trend: [ADX Score]" and "Real Alpha: [BIST vs USD]."
2.  **Sizing Intelligence**: Automatically limits your order size based on the 1% ADV rule.
3.  **Visual Triage**: 🟢 ACTION, 🟡 APPROACHING, ⚪ NEUTRAL.

## ⚔️ Phase 4: The Intraday Execution (The Workflow)
**The Zero-Latency Protocol**:
1.  **Conditional Orders (Süreli Emirler)**: *DEPRECATED*. Do NOT place blind GTC orders the night before.
2.  **Pre-Market Verification**: At 09:40 AM TRT (BIST Pre-Market), manually verify the opening gap. If the stock gaps below your `buy_limit`, DO NOT EXECUTE.
3.  **Capital Parking**: Core and Satellite cash parked in **T+0 PPF (Money Market Funds)**.
4.  **The Trigger**: Once the pre-market gap is verified safe, route the limit order to the broker.

## 🛡️ Phase 5: Maintenance & Predator Audit (Systemic Audit)
1.  **Watchlist Rot Protocol**: Every 90 days, audit the watchlist. Remove stocks that have lost their fundamental edge to prevent survivorship bias.
2.  **The "Market Impact" Check**: Every 30 days, review your fill prices. If your average fill is >0.2% away from your limit, lower the ADV cap from 1% to 0.5%.
3.  **Library Maintenance**: Monthly `pip install --upgrade`.
4.  **Corporate Action Audit**: Mandatory **KAP Check** at 08:40 AM, prior to setting any limits.

---

## ⚖️ Operational Rules
- **Rule 0**: **KAP Chronological Inversion**: Audit KAP disclosures at 08:40 AM strictly before opening the Streamlit dashboard or placing any orders.
- **Rule 1**: **Trend-Only**: No trade if ADX < 20. Do not trade in "Chop."
- **Rule 2**: **Close-Based Stops**: To prevent algorithmic stop-loss hunting, stops are evaluated on an EOD (End of Day) close basis only. Ignore intraday wicks.
- **Rule 3**: **Inflationary Rally Awareness**: If BIST and USD are both rising, verify real corporate growth before aggressively allocating.
- **Rule 4**: **Pre-Market Verification**: Deprecate blind conditional entries. Always verify the 09:40 AM open to prevent executing into gap-down falling knives.
- **Rule 5**: **The 10% Cap**: Diversification is the only defense against "Limit Down" traps.
- **Rule 6**: Math is Sovereign (Python), Execution is Predatory (Conditional).
- **Rule 7**: **Midday Fill Audit**: At 12:30 PM TRT, audit open orders. If an order is <35% filled, cancel the remaining open balance. If the filled portion is <15% of intended size, immediately liquidate the filled shares at Market to prevent trailing orphaned fragments.


