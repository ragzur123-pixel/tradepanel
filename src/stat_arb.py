import logging
import pandas as pd
from data_node import SovereignDataNode

logger = logging.getLogger(__name__)

class StatArbEngine:
    """
    Phase 9 Quantitative Evolution: Delta-Neutral Statistical Arbitrage.
    Instead of buying naked puts (which bleed Theta premium), we hedge by 
    shorting the weakest stock in the same sector while longing the strongest.
    This neutralizes the macro market direction entirely.
    """
    def __init__(self):
        self.node = SovereignDataNode()
        self.sector_pairs = {
            "Aviation": ["THYAO.IS", "PGSUS.IS"],
            "Automotive": ["FROTO.IS", "TOASO.IS"],
            "Banking": ["AKBNK.IS", "YKBNK.IS", "GARAN.IS"],
            "Holding": ["KCHOL.IS", "SAHOL.IS"]
        }

    def scan_pairs(self):
        """
        Scans predefined sectors to find statistically divergent pairs.
        Returns the optimal Long/Short combination to achieve Delta-Neutrality.
        """
        arb_opportunities = []

        for sector, tickers in self.sector_pairs.items():
            if len(tickers) < 2: continue
            
            performance = {}
            for ticker in tickers:
                df = self.node.fetch_bist_data(ticker, period="3mo")
                if df is not None and not df.empty and len(df) > 20:
                    # Calculate 20-day relative strength
                    ret20 = (df['Close'].iloc[-1] - df['Close'].iloc[-20]) / df['Close'].iloc[-20]
                    performance[ticker] = float(ret20)
            
            if len(performance) >= 2:
                # Sort by relative strength
                sorted_perf = sorted(performance.items(), key=lambda x: x[1], reverse=True)
                strongest = sorted_perf[0]
                weakest = sorted_perf[-1]
                
                spread = strongest[1] - weakest[1]
                
                # If the divergence is massive (>15% in 20 days), we bet on Mean Reversion of the Spread
                if spread > 0.15:
                    arb_opportunities.append({
                        "sector": sector,
                        "strategy": "Mean Reversion",
                        "long_leg": weakest[0],  # Buy the laggard
                        "short_leg": strongest[0], # Short the overextended leader
                        "spread_divergence": round(spread * 100, 2),
                        "status": " ARB ZONE"
                    })
                # If the divergence is tight (<5%), we bet on Momentum Expansion
                elif spread > 0 and spread < 0.05:
                    arb_opportunities.append({
                        "sector": sector,
                        "strategy": "Momentum",
                        "long_leg": strongest[0], # Buy the winner
                        "short_leg": weakest[0],  # Short the loser
                        "spread_divergence": round(spread * 100, 2),
                        "status": " WATCHING"
                    })

        return arb_opportunities

if __name__ == "__main__":
    arb = StatArbEngine()
    print("Scanning BIST for Delta-Neutral Arbitrage Pairs...")
    print(arb.scan_pairs())
