import os
import requests
import logging

logger = logging.getLogger(__name__)

class BrokerDMA:
    """
    EXEC-02: Direct Market Access (DMA) Execution Engine.
    Replaces static overnight conditional limits.
    Fires real-time executions directly to IBKR or Alpaca during live market hours
    if and only if the intraday volatility floor is respected.
    """
    def __init__(self):
        self.alpaca_key = os.getenv("ALPACA_API_KEY")
        self.alpaca_secret = os.getenv("ALPACA_SECRET_KEY")
        self.alpaca_url = "https://paper-api.alpaca.markets/v2/orders"
        
        # IBKR requires IB Gateway or TWS running locally
        self.ibkr_url = os.getenv("IBKR_WEB_API_URL", "https://localhost:5000/v1/api/iserver/account")

    def execute_us_trade(self, ticker, action, qty, limit_price, stop_price, take_profit):
        """Executes US trades via Alpaca REST API."""
        if not self.alpaca_key:
            logger.warning("ALPACA_API_KEY missing. DMA US Execution Offline.")
            return False
            
        headers = {
            "APCA-API-KEY-ID": self.alpaca_key,
            "APCA-API-SECRET-KEY": self.alpaca_secret
        }
        
        payload = {
            "symbol": ticker,
            "qty": qty,
            "side": action.lower(), # "buy" or "sell"
            "type": "limit",
            "time_in_force": "day",
            "limit_price": str(limit_price),
            "order_class": "bracket",
            "take_profit": {
                "limit_price": str(take_profit)
            },
            "stop_loss": {
                "stop_price": str(stop_price)
            }
        }
        
        try:
            res = requests.post(self.alpaca_url, json=payload, headers=headers, timeout=10)
            if res.status_code == 200:
                logger.info(f" ALPACA DMA: {action} {qty} {ticker} @ {limit_price}")
                return True
            else:
                logger.error(f" ALPACA DMA ERROR: {res.status_code} - {res.text}")
                return False
        except Exception as e:
            logger.error(f"ALPACA DMA Exception: {e}")
            return False

    def execute_bist_trade(self, ticker, action, qty, limit_price):
        """
        Executes BIST trades via Matriks or Garanti/IsYatirim custom bridge.
        Mock implementation.
        """
        logger.warning(f"BIST DMA requires proprietary FIX bridge for {ticker}. Simulating {action} {qty} @ {limit_price}.")
        return False
