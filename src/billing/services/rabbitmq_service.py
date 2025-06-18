from datetime import datetime, timedelta
import uuid
import json
import logging
import pika
import os


# Configure logging
logger = logging.getLogger(__name__)


class RabbitMQService:
    def __init__(self):
        self.connection = None
        self.channel = None
        self.queue_name = "billing_queue"
        self.queue_name_2 = "plan_queue"
        self.connect()

    def connect(self):
        """Establish connection to RabbitMQ server"""
        try:
            credentials = pika.PlainCredentials(
                username=os.getenv("RABBITMQ_DEFAULT_USER", "rabbit"),
                password=os.getenv("RABBITMQ_DEFAULT_PASS", "docker"),
            )
            parameters = pika.ConnectionParameters(
                host=os.getenv("RABBITMQ_HOST", "rabbitmq"),
                port=5672,
                credentials=credentials,
                heartbeat=600,
                blocked_connection_timeout=300,
            )
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()

            # Declare the queue
            self.channel.queue_declare(queue=self.queue_name, durable=True)
            logger.info(
                f"Successfully connected to RabbitMQ and declared queue '{self.queue_name}'"
            )
            
            # Declare the plan queue
            self.channel.queue_declare(queue=self.queue_name_2, durable=True)
            logger.info(
                f"Successfully connected to RabbitMQ and declared queue '{self.queue_name_2}'"
            )
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            raise

    def publish_message(self, message_type: str, data: dict) -> bool:
        """Publish a message to the queue"""
        try:
            if not self.connection or self.connection.is_closed:
                self.connect()

            message = {"type": message_type, **data}

            # billing queue
            self.channel.basic_publish(
                exchange="",
                routing_key=self.queue_name,
                body=json.dumps(message),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # make message persistent
                ),
            )
            
            # plan queue
            self.channel.basic_publish(
                exchange="",
                routing_key=self.queue_name_2,
                body=json.dumps(message),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # make message persistent
                ),
            )
            
            logger.info(f"Successfully published {message_type} message: {data}")
            return True
        except Exception as e:
            logger.error(f"Failed to publish message to RabbitMQ: {e}")
            return False


# Initialize RabbitMQ service
rabbitmq_service = RabbitMQService()