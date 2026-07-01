# Blueprint: Sovereign Node Dashboard (V1)

## 🏗️ Core Architecture: "The Sentinel"
A high-reliability, low-maintenance trading command center that guides your trades with institutional logic and retail efficiency.

### 1. The Reliability Layer (Backend)
- **Local Python Worker**: Runs on your Home PC (Residential IP).
- **Heartbeat Check**: Before doing anything, the UI checks a `metadata` table. If the data is >24 hours old, the app **Hard-Locks** (Blocks all content) with a "System Stale" warning.
- **Failover Logic**: 
    - Primary: `isyatirimhisse` (Official BIST Data).
    - Failover: `yfinance` (.IS) if Primary is blocked or down.
- **Math Validation**: Scripts will abort and log an error if ATR is 0 or if calculated limits are logically impossible (e.g., Buy Limit > Price).

### 2. The Signal Command Center (UI/UX)
- **Framework**: Streamlit (Mobile-Responsive, hosted on Streamlit Cloud).
- **Signal Presentation**: **Visual Stock Cards**.
    - **Proximity Gauge**: A color-coded bar showing how close the price is to your $SMA - 0.5 \times ATR$ limit.
        - 🟢 **ACTION**: Price is in the Buy/Sell zone.
        - 🟡 **APPROACHING**: Within 1-2% of the limit.
        - ⚪ **NEUTRAL**: Price is far from targets.
- **Position Sizing**: Each card calculates "Suggested Shares" based on a user-defined risk per trade (e.g., "Risk $200 of capital on this trade").

### 3. The Guided Execution Flow
To prevent "Emotional Triggering," the UI enforces a two-step safety gate:
1. **Safety Checklist**: You cannot log a trade until you check three boxes:
    - [ ] **KAP Check**: No disastrous filings? (Link provided in card).
    - [ ] **Macro Check**: No global flash-crash in progress?
    - [ ] **Discipline Check**: Am I following my rules?
2. **One-Tap Journaling**: Once checked, the "LOG ENTRY" button unlocks.
    - One click logs the trade to Supabase.
    - Python instantly calculates your **Exit Target** (Entry + 1.5 * ATR) and populates the "Active Portfolio" tab.

### 4. Implementation Priority (The "No Overwork" Path)
1. **Phase 1 (The Plumbing)**: Local worker script + Supabase table setup.
2. **Phase 2 (The Sentinel)**: Streamlit "Hard-Lock" logic and basic data tables.
3. **Phase 3 (The Signal)**: Visual Cards and Proximity Gauges.
4. **Phase 4 (The Execution)**: Checklist and Journaling integration.

## ⚖️ Terminal Goal
A system that takes **5 minutes of your time per day** (Morning check + Intraday alerts) while ensuring the math is sovereign and the execution is disciplined.
