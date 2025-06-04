import pika
import json
import os
import logging
import time
from typing import Callable, Any

logger = logging.getLogger(__name__)

class RabbitMQClient:
    def __init__(self):
        self.connection = None
        self.channel = None
        self.connect_with_retry()

    def connect_with_retry(self, max_retries=5, retry_delay=5):
        """Establish connection to RabbitMQ server with retry mechanism"""
        for attempt in range(max_retries):
            try:
                logger.info(f"Connection attempt {attempt + 1} of {max_retries}")
                self.connect()
                return
            except Exception as e:
                logger.error(f"Connection attempt {attempt + 1} failed: {str(e)}")
                if attempt < max_retries - 1:
                    logger.info(f"Waiting {retry_delay} seconds before next attempt...")
                    time.sleep(retry_delay)
                else:
                    logger.error("Max retries reached. Giving up.")
                    raise

    def connect(self):
        """Establish connection to RabbitMQ server"""
        try:
            credentials = pika.PlainCredentials(
                os.getenv('RABBITMQ_DEFAULT_USER', 'rabbit'),
                os.getenv('RABBITMQ_DEFAULT_PASS', 'docker')
            )
            parameters = pika.ConnectionParameters(
                host=os.getenv('RABBITMQ_HOST', 'rabbitmq'),
                credentials=credentials,
                heartbeat=600,
                blocked_connection_timeout=300
            )
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            logger.info("Successfully connected to RabbitMQ")
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {str(e)}")
            raise

    def declare_queue(self, queue_name: str):
        """Declare a queue if it doesn't exist"""
        try:
            queue_args = {
                'x-message-ttl': 60000,  
                'x-max-length': 100,   
                'x-dead-letter-exchange': 'dlx',
                'x-dead-letter-routing-key': f'{queue_name}-dead'
            }
            self.channel.queue_declare(queue=queue_name, durable=True, arguments=queue_args)
            logger.info(f"Queue {queue_name} declared successfully")
        except Exception as e:
            logger.error(f"Failed to declare queue {queue_name}: {str(e)}")
            raise

    def publish_message(self, queue_name: str, message: dict):
        """Publish a message to a queue"""
        try:
            self.channel.basic_publish(
                exchange='',
                routing_key=queue_name,
                body=json.dumps(message),
                properties=pika.BasicProperties(
                    delivery_mode=2, 
                )
            )
            logger.info(f"Message published to queue {queue_name}")
        except Exception as e:
            logger.error(f"Failed to publish message to queue {queue_name}: {str(e)}")
            raise

    def consume_messages(self, queue_name: str, callback: Callable[[str, Any], None]):
        """Start consuming messages from a queue"""
        try:
            self.channel.basic_qos(prefetch_count=1)
            self.channel.basic_consume(
                queue=queue_name,
                on_message_callback=callback
            )
            logger.info(f"Started consuming messages from queue {queue_name}")
            self.channel.start_consuming()
        except Exception as e:
            logger.error(f"Failed to consume messages from queue {queue_name}: {str(e)}")
            raise

    def close(self):
        """Close the connection to RabbitMQ"""
        if self.connection and not self.connection.is_closed:
            self.connection.close()
            logger.info("RabbitMQ connection closed")

rabbitmq_client = RabbitMQClient() 