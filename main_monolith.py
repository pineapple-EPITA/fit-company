#!/usr/bin/env python
import threading
from src.fit.app import app
from src.fit.queue_consumer import run_consumer
def start_premium_plan_consumer():
    consumer_thread = threading.Thread(target=run_consumer, daemon=True)
    consumer_thread.start()

if __name__ == "__main__":
    start_premium_plan_consumer()
    app.run(host="0.0.0.0", port=5000, debug=True) 