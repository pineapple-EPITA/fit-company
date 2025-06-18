#!/usr/bin/env python
import os
import sys
sys.path.append('/app')

from src.fit.queue_consumer import run_consumer

if __name__ == "__main__":
    print("Testing SAGA consumer...")
    try:
        run_consumer()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc() 