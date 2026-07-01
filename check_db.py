import os
from db_manager import SupabaseManager

try:
    db = SupabaseManager()
    watchlist = db.get_watchlist()
    gamblers = [t for t in watchlist if t.get('bucket') == 'GAMBLER']
    
    print("--- WATCHLIST STATUS ---")
    print(f"Total Tickers: {len(watchlist)}")
    print(f"GAMBLER Bucket Count: {len(gamblers)}")
    for g in gamblers:
        print(f" - {g.get('ticker')}")
        
except Exception as e:
    print(f"Error checking DB: {e}")
