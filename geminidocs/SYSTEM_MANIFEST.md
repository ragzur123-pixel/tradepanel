# 🧠 SYSTEM INTELLIGENCE MANIFEST: Sovereign Node (Execution Terminal - 2026)

> **FOR AI AGENTS**: This system operates under a fundamentally different paradigm than HFT algorithms. The Sovereign Node is a **Bi-Modal Portfolio Management Panel & Risk Desk**. It relies on sovereign mathematical analysis to provide perfect execution targets, while leaving final execution authority to the human operator via conditional broker routing. 

---

## 🏁 1. SYSTEM PHILOSOPHY: The Zero-Latency Human Operator
The Sovereign Node acts as an execution command center. It bridges the gap between institutional-grade quantitative filtering and retail execution efficiency. It aggressively filters out market noise, macro devaluation, and psychological bias to guide trades perfectly.

### Core Strategic Pillars:
*   **Math-Sovereign Targets**: Rejects "gut feeling." All entries and exits are calculated via rigid standard-deviations (ATR) and rolling regressions (SMA).
*   **Bi-Modal Allocation**: Strict enforcement of the **70/30 Doctrine**:
    *   **🛡️ The Core (70%)**: Deep pullbacks (`SMA20 - 0.5 * ATR14`) on ultra-liquid, blue-chip foundations.
    *   **🚀 The Satellite (30%)**: Aggressive momentum setups (`SMA20 - 1.0 * ATR14`) strictly governed by spread limits.
    *   *(Optional)* **🎲 The Gambler (5% Cap)**: Quarantined arbitrage & speculative setups monitored for extreme risk.
*   **Zero-Latency Execution Workflow**: Human latency is eliminated by setting **Conditional Orders** at the broker level the night before based on the Node's calculations.
*   **Predatory Scaling**: Capping position size intrinsically to **1% of the Average Daily Value (ADV)** to ensure orders do not slip the bid-ask matrix.

---

## 🛠️ 2. HARDENED ARCHITECTURAL MODULES

### A. The Engine (Data & Math Worker)
*   **`src/worker.py`**: The heavy-lifting backend node. Runs asynchronously (or via cron/task scheduler) to crunch BIST/US tickers. 
*   **`src/data_node.py` & `src/indicators.py`**: The math pipeline. Integrates:
    *   **ADX Trend Veto**: Drops trades in choppy regimes (`ADX < 20`).
    *   **Real Alpha Filter**: Audits nominal stock returns against USD/TRY capital flows to prevent illusory gains.
    *   **Tick-Rounding Accuracy**: Formats all prices to the precise sub-penny exchange thresholds for the target ticker to prevent order rejection.

### B. The Command Center (UI/UX)
*   **`src/app.py`**: The Streamlit Terminal.
    *   **Apple-Inspired Aesthetics**: No clunky elements. Full-width native components and responsive Proximity Gauges (🟢 Action, 🟡 Approaching, ⚪ Neutral).
    *   **System Sync Heartbeat**: Constantly monitors Supabase `metadata`. If the engine timestamp is stale, it hard-locks the UI to prevent execution on dead math.
    *   **Dynamic Rebalancer**: Live visualization of the 70/30 allocation matrix, displaying drift metrics and risk ceiling breaches in real-time.

---

## 📐 3. QUANTITATIVE HARDENING (The "Ground Truth")
1.  **Regime Awareness**: Tracks BIST and SPY against SMA(50) benchmarks. Halves sizing algorithmic limits dynamically if a BEAR regime triggers.
2.  **Tail-Risk Detection**: Continuously scans open vector exposure and actively flags the need for VIOP Index Put options when naked exposure gets dangerously high.
3.  **End-of-Day Stop Logic**: Stop-Losses are calculated but executed only on a closing basis to completely neutralize algorithmic stop-hunting (wicking) by institutional MMs.
4.  **Watchlist Rot**: Internal database auditing highlights tickers un-traded for 90+ days, prompting a fundamental cull to avoid database pollution and survivorship bias.

---

## 🚀 4. TERMINAL ROADMAP STATUS: ARCHITECTURAL FINALITY ✅

### 🛡️ Phase 1: The Cloud Foundation (COMPLETE)
- [x] **Supabase Sync**: Real-time Postgres synchronization for universal mobile/desktop access.
- [x] **Heartbeat Guard**: Established the `last_success` kill-switch.

### 🛡️ Phase 2: Engine Predation (COMPLETE)
- [x] **Bi-Modal Math Integration**: Separate equations mapped to CORE and SATELLITE assets.
- [x] **ADV Market Impact Filters**: Integrated live volume scaling.

### 🛡️ Phase 3: UI/UX Masterpiece (COMPLETE)
- [x] **Layout Unification**: Shifted to a single-pane dashboard, removing page clutter.
- [x] **Expander Overhaul**: Designed ultra-premium System Control modules without emojis.
- [x] **Decoupled Refresh Logic**: Background threading for `worker.py` via the Streamlit manual Refresh button.

---

## ⚠️ 5. OPERATIONAL CONSTRAINTS
*   **Capital Parking**: 100% of uninvested Core/Satellite cash must live in Money Market Funds (PPF) overnight.
*   **KAP Gate**: A manual Public Disclosure Platform (KAP) check is required before logging *any* triggered conditional.
*   **Deployment Vector**: Optimized for **Streamlit Cloud** targeting real-time mobile push environments.

---
*Final Intelligence Manifest - Revised 2026-06-20 - Ground Truth Established.*
