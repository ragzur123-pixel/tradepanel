import os
from dotenv import load_dotenv
from supabase import create_client, Client
from datetime import datetime, timezone
import pandas as pd
import logging

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SovereignDatabase:
    def __init__(self):
        load_dotenv()
        url: str = os.environ.get("SUPABASE_URL")
        key: str = os.environ.get("SUPABASE_KEY")
        if not url or not key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in .env")
        self.supabase: Client = create_client(url, key)

    def update_heartbeat(self, status="OK", error_msg=None, bist_regime='NEUTRAL', us_regime='NEUTRAL', bist_adx=0.0, us_adx=0.0, usd_try_trend='NEUTRAL', circuit_breaker='SAFE'):
        """Updates the sentinel heartbeat and market regime in Supabase."""
        data = {
            "last_success": datetime.now(timezone.utc).isoformat(),
            "worker_status": status,
            "error_log": error_msg,
            "bist_regime": bist_regime,
            "us_regime": us_regime,
            "bist_adx": float(bist_adx),
            "us_adx": float(us_adx),
            "usd_try_trend": usd_try_trend,
            "circuit_breaker": circuit_breaker
        }
        # Assuming we have a 'metadata' table with a single row (id=1)
        try:
            self.supabase.table("metadata").upsert({"id": 1, **data}).execute()
            logger.info(f"Heartbeat & Regime updated: {status}")
        except Exception as e:
            logger.error(f"Failed to update heartbeat: {e}")

    def push_limits(self, limits_df: pd.DataFrame):
        """Pushes calculated Buy/Sell limits to the database."""
        try:
            # Sanitize Data: JSON cannot handle NaN or Infinity.
            # Convert NaNs to None (null in JSON) to prevent Supabase 400 Bad Request errors.
            limits_df = limits_df.replace({pd.NA: None, float('nan'): None})
            if 'slippage_risk_pct' in limits_df.columns:
                limits_df = limits_df.drop(columns=['slippage_risk_pct'])
            
            # Convert DF to list of dicts for Supabase
            records = limits_df.to_dict('records')
            
            # SYNC-01 & SYNC-04: Ghost Limits Garbage Collector Repair
            existing_res = self.supabase.table("limits").select("ticker").execute()
            existing_tickers = [row['ticker'] for row in existing_res.data] if existing_res.data else []
            
            wl_res = self.supabase.table("watchlist").select("ticker").execute()
            wl_tickers = set(row['ticker'] for row in wl_res.data) if wl_res.data else set()
            
            orphaned_tickers = [t for t in existing_tickers if t not in wl_tickers]
            
            if orphaned_tickers:
                logger.info(f"SYNC-01: Purging {len(orphaned_tickers)} orphaned setups: {orphaned_tickers}")
                self.supabase.table("limits").delete().in_("ticker", orphaned_tickers).execute()

            # Upsert new limits
            self.supabase.table("limits").upsert(records).execute()
            logger.info(f"Pushed {len(records)} limits to Supabase.")
        except Exception as e:
            logger.error(f"Failed to push limits: {e}")
            self.update_heartbeat(status="ERROR", error_msg=str(e))

    def get_watchlist(self):
        """Retrieves the active watchlist from Supabase."""
        try:
            response = self.supabase.table("watchlist").select("*").execute()
            return response.data
        except Exception as e:
            logger.error(f"Failed to fetch watchlist: {e}")
            return []

    def get_open_portfolio(self):
        """Retrieves currently open positions from the portfolio to prevent double-dipping."""
        try:
            response = self.supabase.table("portfolio").select("ticker").eq("status", "OPEN").execute()
            return [row["ticker"] for row in response.data] if response.data else []
        except Exception as e:
            logger.error(f"Failed to fetch open portfolio: {e}")
            return []
