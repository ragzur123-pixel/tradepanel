# TradePanel Philosophy & Directives

<RULE>
## The "Bloomberg Panel" Paradigm
**Directive:** Do NOT attempt to automate the execution/purchase step using broker APIs (e.g., Alpaca, IBKR) or Selenium web-scraping macros. 
**Rationale:** 
- API costs (Alpaca) are high and execution environments are unreliable ("they give you the dip").
- Web scraping/macros for portal execution are highly risky and not worth the engineering or financial risk.

**Core Purpose:** This system is NOT a High-Frequency Trading (HFT) bot. It is a highly advanced **Decision Support System (A "Bloomberg Panel")**. 
- Its purpose is to provide institutional-grade risk calculations, portfolio management, and precise Buy/Sell limits. 
- The user will execute the trades manually based on the panel's advice.
- Missing a trade because the user was asleep/away is **acceptable**. The goal is not a high "Win Rate" (catching every setup), but a massive **Win Size** (ensuring the trades we *do* catch are highly profitable and mathematically sound).
</RULE>
