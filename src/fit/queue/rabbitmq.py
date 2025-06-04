import pika
import json
import os
import logging
import time
from typing import Callable, Any, Dict
from pydantic import BaseModel, ValidationError
from datetime import date

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WodMessage(BaseModel):
    user_email: str
    date: str

class RabbitMQClient:
    def __init__(self):
        self.connection = None
        self.channel = None
        self.queue_name = 'createWodQueue'
        self.dlq_name = f'{self.queue_name}-dead'
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
        """Establish connection to RabbitMQ server and declare queues"""
        try:
            host = os.getenv('RABBITMQ_HOST', 'rabbitmq')
            user = os.getenv('RABBITMQ_DEFAULT_USER', 'rabbit')
            password = os.getenv('RABBITMQ_DEFAULT_PASS', 'docker')
            
            logger.info(f"Attempting to connect to RabbitMQ at {host} with user {user}")
            
            credentials = pika.PlainCredentials(user, password)
            parameters = pika.ConnectionParameters(
                host=host,
                credentials=credentials,
                heartbeat=600,
                blocked_connection_timeout=300,
                connection_attempts=3,
                retry_delay=5
            )
            
            logger.info("Connection parameters configured, attempting to establish connection...")
            self.connection = pika.BlockingConnection(parameters)
            logger.info("Connection established successfully")
            
            self.channel = self.connection.channel()
            logger.info("Channel created successfully")

            logger.info("Declaring dead letter exchange...")
            self.channel.exchange_declare(exchange='dlx', exchange_type='direct', durable=True)
            
            logger.info(f"Declaring dead letter queue: {self.dlq_name}")
            self.channel.queue_declare(queue=self.dlq_name, durable=True)
            
            logger.info("Binding dead letter queue to exchange...")
            self.channel.queue_bind(
                exchange='dlx',
                queue=self.dlq_name,
                routing_key=self.dlq_name
            )

            arguments = {
                'x-message-ttl': 60000,  # 1 minute in ms
                'x-max-length': 100,
                'x-dead-letter-exchange': 'dlx',
                'x-dead-letter-routing-key': self.dlq_name
            }
            
            logger.info(f"Declaring main queue: {self.queue_name}")
            self.channel.queue_declare(
                queue=self.queue_name,
                durable=True,
                arguments=arguments
            )
            logger.info(f"Queues '{self.queue_name}' and '{self.dlq_name}' declared successfully")
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {str(e)}")
            logger.error(f"Connection details - Host: {host}, User: {user}")
            raise

    def validate_message(self, message: Dict[str, Any]) -> WodMessage:
        """Validate message format"""
        return WodMessage(**message)

    def publish_message(self, message: dict):
        """Publish a message to the queue after validation"""
        try:
            validated_message = self.validate_message(message)
            self.channel.basic_publish(
                exchange='',
                routing_key=self.queue_name,
                body=validated_message.model_dump_json(),
                properties=pika.BasicProperties(
                    delivery_mode=2,
                    content_type='application/json',
                    headers={'x-retry-count': 0}  # Initialize retry count
                )
            )
            logger.info(f"Message published to queue {self.queue_name}")
        except ValidationError as ve:
            logger.error(f"Message validation failed: {ve}")
            raise
        except Exception as e:
            logger.error(f"Failed to publish message to queue {self.queue_name}: {str(e)}")
            raise

    def close(self):
        """Close the connection to RabbitMQ"""
        if self.connection and not self.connection.is_closed:
            self.connection.close()
            logger.info("RabbitMQ connection closed")

rabbitmq_client = RabbitMQClient() 