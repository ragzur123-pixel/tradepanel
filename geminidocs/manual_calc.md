# Sovereign Node: Manual Backup Protocol

This document serves as your emergency fail-safe. If `isyatirimhisse` or `yfinance` breaks due to website changes, your Supabase dashboard will hard-lock to prevent you from using stale data. 

**Do not panic.** You are the ultimate bot. You can calculate the exact limits manually using TradingView in under 60 seconds.

## The Mathematical Formulas

### Core Protocol (The Tank)
**Rules**: Capital must be 70%. Stock must be ABOVE the 200 SMA on the Daily chart.
*   **Buy Target**: `SMA(20) - (0.5 * ATR(14))`
*   **Front-Run Limit**: `Buy Target * 0.999` (Then round to nearest valid BIST tick)
*   **Sell Target**: `Buy Target + (1.5 * ATR(14))` (Then multiply by `0.997` for friction)
*   **Hard Stop**: `Buy Target - (1.0 * ATR(14))`

### Satellite Protocol (The Sniper)
**Rules**: Capital must be 30%. Spread must be < 0.5%. ADX(14) must be > 20.
*   **Buy Target**: `SMA(20) - (1.0 * ATR(14))`
*   **Front-Run Limit**: `Buy Target * 0.999` (Then round to nearest valid BIST tick)
*   **Sell Target**: `Buy Target + (1.5 * ATR(14))` (Then multiply by `0.997` for friction)
*   **Hard Stop**: `Buy Target - (1.0 * ATR(14))`

---

## Step-by-Step Manual Calculation on TradingView

1.  Open **TradingView** (Free account is fine).
2.  Open the chart for your target stock (e.g., `THYAO`).
3.  Set the timeframe to **1D (Daily)**.
4.  Add the **"Moving Average Simple" (SMA)** indicator. Set Length to **20**.
5.  Add the **"Average True Range" (ATR)** indicator. Set Length to **14**, Smoothing to RMA.
6.  Look at the values for the *Previous Day's* completed candle.
    *   *Example*: SMA is `300`. ATR is `10`.
7.  **Calculate (Core Example)**:
    *   `300 - (0.5 * 10) = 295` (This is your raw Buy Target).
    *   `295 * 0.999 = 294.705` (Round to tick: `294.75`).
    *   **Place your Limit Buy Order at 294.75.**

## Maintenance Fix

Once the trading day is over, open your terminal and run:
```bash
pip install --upgrade isyatirimhisse yfinance pandas
```
If the libraries have been patched by their maintainers, this will fix the scraper. If it still fails, check the GitHub repositories for those projects for open issues.
