import json
import pika
from .fitness_coach_service import request_wod
import logging
import os


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logging.getLogger("pika").setLevel(logging.DEBUG)


QUEUE_NAME = "createWodQueue"

def callback(ch, method, properties, body):
    logging.info(f"[Consumer] Received message: {body}")
    try:
        data = json.loads(body)
        user_email = data.get("user_email")
        if user_email:
            request_wod(user_email)  
            logging.info(f"[Consumer] WOD generated for {user_email}")
            ch.basic_ack(delivery_tag=method.delivery_tag)
        else:
            logging.info("[Consumer] Missing user_email")
    except Exception as e:
        logging.info(f"[Consumer] Error processing message: {str(e)}")

def start_consumer():
    logging.info("Consumer thread started")
    credentials = pika.PlainCredentials(
        username=os.getenv("RABBITMQ_DEFAULT_USER"),
        password=os.getenv("RABBITMQ_DEFAULT_PASS")
    )   
    parameters = pika.ConnectionParameters(
        host=os.getenv("RABBITMQ_HOST"),
        port=5672,
        credentials=credentials,
        heartbeat=600,
        blocked_connection_timeout=300
    ) 
    
    connection = pika.BlockingConnection(parameters)    
    channel = connection.channel()

    channel.queue_declare(
        queue=QUEUE_NAME,
        durable=True,
        arguments={
            "x-message-ttl": 60000,
            "x-max-length": 100,
            "x-dead-letter-exchange": "dlx",
            "x-dead-letter-routing-key": f"{QUEUE_NAME}-dead"
        }
    )
    logging.info(f"[Consumer] Waiting for messages in '{QUEUE_NAME}'...")

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback, auto_ack=False)

    channel.start_consuming()