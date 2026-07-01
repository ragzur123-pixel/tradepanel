import schedule
import time
import subprocess
import os
import logging
from datetime import datetime
import pytz

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

def run_worker():
    # Only run if BIST is open or it's EOD processing (roughly 09:55 to 18:15 TRT, plus midnight)
    trt = pytz.timezone('Europe/Istanbul')
    now = datetime.now(trt)
    
    # BIST Market Hours: 10:00 to 18:10. We also want an EOD run at 00:00.
    is_market_open = (now.weekday() < 5) and ((now.hour >= 10 and now.hour < 18) or (now.hour == 18 and now.minute <= 15))
    is_midnight = (now.hour == 0 and now.minute < 30)
    
    if is_market_open or is_midnight:
        logger.info(f"Running Sovereign Node Intraday/EOD Engine. Current TRT time: {now.strftime('%H:%M')}")
        try:
            subprocess.run(["python", "src/worker.py"], check=True)
        except subprocess.CalledProcessError as e:
            logger.error(f"Worker crashed: {e}")
    else:
        logger.info(f"Market Closed. Skipping worker run. Current TRT time: {now.strftime('%H:%M')}")

# Schedule the worker to run every 30 minutes to catch Intraday News and Macro Regime shifts
# This defeats the "Rearview Mirror" flaw of EOD-only polling.
schedule.every(30).minutes.do(run_worker)

if __name__ == '__main__':
    logger.info("☁️ Sovereign Cloud Node Initialized.")
    logger.info("Polling every 30 minutes during BIST market hours to update Live Portfolio Limits...")
    
    # Run once immediately on startup
    run_worker()
    
    while True:
        schedule.run_pending()
        time.sleep(60)
