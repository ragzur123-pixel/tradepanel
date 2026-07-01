import os
import sys

# Ensure src is in path
sys.path.append(os.path.join(os.getcwd(), 'src'))

from worker import main

if __name__ == "__main__":
    main()
