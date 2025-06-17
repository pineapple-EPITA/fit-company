import os
import json
import logging
import pika
from .services.billing_service import BillingService

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def process_message(ch, method, properties, body):
    """Process incoming messages from the queue"""
    try:
        message = json.loads(body)
        logger.info(f"Received message: {message}")

        # Handle different message types
        if message.get('type') == 'subscription_expiring':
            # Get expiring subscriptions
            days = message.get('days', 7)
            expiring_subs = BillingService.check_expiring_subscriptions(days)
            logger.info(f"Found {len(expiring_subs)} expiring subscriptions")
            
            # Here you would typically send notifications to users
            # This could be implemented later when adding notification features

        elif message.get('type') == 'subscription_cancelled':
            subscription_id = message.get('subscription_id')
            if subscription_id:
                subscription = BillingService.cancel_subscription(subscription_id)
                logger.info(f"Cancelled subscription: {subscription}")

        # Acknowledge the message
        ch.basic_ack(delivery_tag=method.delivery_tag)

    except json.JSONDecodeError as e:
        logger.error(f"Error decoding message: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag)
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag)

def run_consumer():
    """Run the queue consumer"""
    try:
        # Get RabbitMQ connection details from environment
        rabbitmq_host = os.getenv('RABBITMQ_HOST', 'localhost')
        rabbitmq_user = os.getenv('RABBITMQ_DEFAULT_USER', 'guest')
        rabbitmq_pass = os.getenv('RABBITMQ_DEFAULT_PASS', 'guest')

        # Create connection
        credentials = pika.PlainCredentials(rabbitmq_user, rabbitmq_pass)
        parameters = pika.ConnectionParameters(
            host=rabbitmq_host,
            credentials=credentials
        )
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()

        # Declare queues
        channel.queue_declare(queue='billing_queue', durable=True)
        channel.queue_declare(queue='subscription_notifications', durable=True)

        # Set up consumer
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(
            queue='billing_queue',
            on_message_callback=process_message
        )

        logger.info("Starting to consume messages...")
        channel.start_consuming()

    except pika.exceptions.AMQPConnectionError as e:
        logger.error(f"Failed to connect to RabbitMQ: {e}")
        # You might want to implement retry logic here
    except Exception as e:
        logger.error(f"Error in consumer: {e}")
    finally:
        if 'connection' in locals() and connection.is_open:
            connection.close() 