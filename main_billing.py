#!/usr/bin/env python
import threading
import logging
from src.billing.app import run_app
from src.billing.queue_consumer import run_consumer

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def start_consumer():
    """Start the queue consumer in a separate thread"""
    try:
        consumer_thread = threading.Thread(target=run_consumer, daemon=True)
        consumer_thread.start()
        logger.info("Queue consumer thread started successfully")
    except Exception as e:
        logger.error(f"Failed to start queue consumer: {e}")
        # Continue with Flask app even if consumer fails

if __name__ == "__main__":
    try:
        # Start the queue consumer in a separate thread
        start_consumer()
        
        # Start the Flask app in the main thread
        logger.info("Starting Flask app...")
        run_app()
    except Exception as e:
        logger.error(f"Failed to start billing service: {e}")
        raise 