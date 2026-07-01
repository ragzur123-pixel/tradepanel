import logging
from db_manager import SovereignDatabase

logger = logging.getLogger("bayesian_audit")

class BayesianSelfAuditor:
    """
    Calibrates AI Confidence (Subjective) to Realized Win Rates (Empirical).
    Ensures the Kelly formula uses reality, not model optimism.
    """
    def __init__(self, db: SovereignDatabase):
        self.db = db
        # 1=GAMBLER, 2=SATELLITE, 3=CORE
        self.base_win_rates = {"GAMBLER": 0.40, "SATELLITE": 0.48, "CORE": 0.60}

    def get_realized_edge(self):
        """Calculates win rates per bucket from the last closed trades."""
        # For Sovereign Node, we query closed trades from the portfolio table
        try:
            response = self.db.supabase.table("portfolio").select("*").eq("status", "CLOSED").execute()
            history = response.data if response and response.data else []
        except Exception as e:
            logger.error(f"BAYESIAN AUDIT: Failed to fetch history: {e}")
            history = []
            
        if not history: return self.base_win_rates
        
        realized_rates = {}
        for bucket, base_rate in self.base_win_rates.items():
            level_trades = [t for t in history if t.get("bucket", "CORE") == bucket]
            if len(level_trades) < 5:
                realized_rates[bucket] = base_rate
                continue
                
            # PRTF-04: The Bayesian Time Bomb Defusal
            # Assume a trade is a 'Win' if net_pnl > 0 or exit_price > entry_price
            wins = sum(1 for t in level_trades if t.get("net_pnl", 0) > 0 or float(t.get("exit_price") or 0.0) > float(t.get("entry_price") or 0.0))
            rate = wins / len(level_trades)
            
            # BLENDING: 50% Realized, 50% Base (Bayesian prior)
            weight = min(1.0, len(level_trades) / 50) # Full weight at 50 trades
            blended = (rate * weight) + (base_rate * (1 - weight))
            
            realized_rates[bucket] = round(blended, 3)
            logger.info(f"BAYESIAN UPDATE: {bucket} Win Rate calibrated to {blended:.1%}")
            
        return realized_rates
