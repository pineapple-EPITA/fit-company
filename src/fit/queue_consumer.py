import os
import pika
import json
import logging
from typing import Dict, Any
from .services.user_service import update_user_plan

logger = logging.getLogger(__name__)

# Disable pika logging 
logging.getLogger("pika").setLevel(logging.WARNING)

class BillQueueConsumer:
    _instance = None
    _is_initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(BillQueueConsumer, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._is_initialized:
            self.connection = None
            self.channel = None
            self.queue_name = "plan_queue"
            self._is_initialized = True
            self.connect()

    def ensure_connection(self):
        """Ensure connection is established"""
        if not self.connection or self.connection.is_closed:
            self.connect()

    def connect(self):
        """Establish connection to RabbitMQ server"""
        logger.debug("Attempting to connect to RabbitMQ")
        credentials = pika.PlainCredentials(
            username=os.getenv("RABBITMQ_DEFAULT_USER", "rabbit"),
            password=os.getenv("RABBITMQ_DEFAULT_PASS", "docker")
        )
        parameters = pika.ConnectionParameters(
            host=os.getenv("RABBITMQ_HOST", "rabbitmq"),
            port=5672,
            credentials=credentials,
            heartbeat=600,
            blocked_connection_timeout=300
        )
        self.connection = pika.BlockingConnection(parameters)
        self.channel = self.connection.channel()
        
        arguments = {
            "x-message-ttl": 60000,  # 1 minute
            "x-max-length": 100,
            "x-dead-letter-exchange": "dlx",  # Dead Letter Exchange
            "x-dead-letter-routing-key": f"{self.queue_name}-dead"
        }
        
        
        # Declare the Dead Letter Exchange and Queue
        self.channel.exchange_declare(exchange="dlx", exchange_type="direct")
        self.channel.queue_declare(queue=f"{self.queue_name}-dead", durable=True)
        self.channel.queue_bind(
            exchange="dlx",
            queue=f"{self.queue_name}-dead",
            routing_key=f"{self.queue_name}-dead"
        )

        # Declare the main queue
        self.channel.queue_declare(
            queue=self.queue_name,
            durable=True,
            arguments=arguments
        )
        logger.info(f"Successfully connected to RabbitMQ and declared queue '{self.queue_name}'")

    def start_premium_plan_consumer(self, ch, method, properties, body):
        """Handle received messages"""
        
        try:
            logger.info(f"Received message from {self.queue_name}: {body}")
            message = json.loads(body)
            user_email = message.get("user_email")
            sub_type = message.get("type")
            if not user_email or not sub_type:
                logger.warning("Invalid message: missing user_email or type")
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
                return
            
            update_user_plan(user_email, sub_type)  
            ch.basic_ack(delivery_tag=method.delivery_tag)
        
        
        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode message: {str(e)}")
            # Don't requeue if the message is malformed
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        except Exception as e:
            logger.error(f"Unexpected error processing message: {str(e)}", exc_info=True)
            # Requeue only for unexpected errors
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

    def start_consuming(self):
        """Start consuming messages from the queue"""
        try:
            logger.info("Starting RabbitMQ consumer")
            self.ensure_connection()
            
            # Set up consumer with QoS
            self.channel.basic_qos(prefetch_count=1)
            self.channel.basic_consume(
                queue=self.queue_name,
                on_message_callback=self.start_premium_plan_consumer
            )
            
            logger.info(f"Started consuming from queue '{self.queue_name}'")
            self.channel.start_consuming()
            
        except KeyboardInterrupt:
            logger.info("Received shutdown signal, stopping consumer...")
            self.stop()
        except Exception as e:
            logger.error(f"Error in consumer: {str(e)}", exc_info=True)
            self.stop()

    def stop(self):
        """Stop the consumer and close connection"""
        try:
            if self.channel and self.channel.is_open:
                self.channel.stop_consuming()
                logger.info("Stopped consuming messages")
            
            if self.connection and not self.connection.is_closed:
                self.connection.close()
                logger.info("Closed RabbitMQ connection")
        except Exception as e:
            logger.error(f"Error while stopping consumer: {str(e)}", exc_info=True)


def run_consumer():
    # Create a singleton instance
    bill_queue_consumer = BillQueueConsumer()
    """Entry point to start the consumer"""
    # try:
    logger.info("Starting consumer")
    print("Starting consumer")
    bill_queue_consumer.start_consuming()
