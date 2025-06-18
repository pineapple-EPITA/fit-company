#!/usr/bin/env python
import threading
from src.fit.app import run_app
from src.fit.queue_consumer import run_consumer
def start_premium_plan_consumer():
    print("Starting premium plan consumer...")
    consumer_thread = threading.Thread(target=run_consumer, daemon=True)
    consumer_thread.start()

if __name__ == "__main__":
    start_premium_plan_consumer()
    run_app()