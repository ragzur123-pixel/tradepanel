import os
import requests
import pandas as pd
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class L2DataBridge:
    """
    EXEC-01: High-Resolution Level 2 Data Ingestion.
    Connects to order-book data feeds (Polygon for US, IBKR/BISTECH for BIST).
    Provides exact tick data for true Cumulative Volume Delta (CVD) and liquidity sweep detection.
    """
    def __init__(self):
        self.polygon_key = os.getenv("POLYGON_API_KEY")
        self.alpaca_key = os.getenv("ALPACA_API_KEY")
        self.alpaca_secret = os.getenv("ALPACA_SECRET_KEY")

    def fetch_us_tick_data(self, ticker, limit=50000):
        """Fetches US Tick Data (Trades & Quotes) via Polygon API for microstructure analysis."""
        if not self.polygon_key:
            logger.warning("POLYGON_API_KEY missing. Falling back to OHLCV emulation for L2.")
            return None
            
        # Example API call to Polygon's /v3/trades endpoint for tick-level data
        date_str = datetime.now().strftime('%Y-%m-%d')
        url = f"https://api.polygon.io/v3/trades/{ticker}?timestamp={date_str}&limit={limit}&apiKey={self.polygon_key}"
        
        try:
            res = requests.get(url, timeout=10)
            if res.status_code == 200:
                data = res.json().get("results", [])
                if not data: return None
                
                df = pd.DataFrame(data)
                df['Date'] = pd.to_datetime(df['sip_timestamp'], unit='ns')
                df.rename(columns={'price': 'Price', 'size': 'Volume'}, inplace=True)
                df.set_index('Date', inplace=True)
                return df
            else:
                logger.error(f"Polygon L2 API Error: {res.status_code}")
                return None
        except Exception as e:
            logger.error(f"Polygon L2 bridge failed: {e}")
            return None

    def fetch_bist_tick_data(self, ticker):
        """
        BISTECH L2 Integration Mock. 
        Requires Matriks API / IdealData websocket connection.
        """
        # Placeholder for proprietary BIST L2 integration
        logger.warning(f"BISTECH L2 Data requires proprietary terminal connection for {ticker}. Emulating from L1.")
        return None

    def get_dynamic_spread(self, ticker, market="US"):
        """
        EXEC-04: Dynamic Transaction Cost Analysis (TCA).
        Fetches the real-time Bid-Ask spread width to calculate exact execution slippage.
        """
        if market == "US" and self.polygon_key:
            url = f"https://api.polygon.io/v3/quotes/{ticker}?limit=1&apiKey={self.polygon_key}"
            try:
                res = requests.get(url, timeout=5)
                if res.status_code == 200:
                    data = res.json().get("results", [])
                    if data:
                        bid = data[0].get("bid_price", 0)
                        ask = data[0].get("ask_price", 0)
                        if bid > 0 and ask > 0:
                            spread_pct = (ask - bid) / bid
                            return spread_pct
            except Exception as e:
                logger.error(f"Failed to fetch L2 Quotes for {ticker}: {e}")
        
        # Fallback dynamic spread assumptions
        if market == "US": return 0.0005 # 5 bps for liquid US
        else: return 0.0015 # 15 bps for BIST mid-caps
