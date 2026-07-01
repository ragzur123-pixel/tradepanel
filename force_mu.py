import sys
import os
import pandas as pd
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from data_node import SovereignDataNode
from db_manager import SovereignDatabase

def force_process():
    print("Forcing processing for MU as CORE...")
    node = SovereignDataNode()
    limits = node.calculate_sovereign_limits("MU", "US", "CORE")
    if limits:
        db = SovereignDatabase()
        db.push_limits(pd.DataFrame([limits]))
        print("Successfully pushed MU to database as CORE!")
    else:
        print("Failed to calculate limits for MU.")

if __name__ == "__main__":
    force_process()
