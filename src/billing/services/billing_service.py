from datetime import datetime, timedelta
import uuid
import json
import logging
import pika
import os
from typing import Optional, List
from ..database import db_session
from ..models_db import SubscriptionModel, PaymentModel, SubscriptionStatus
from ..models_dto import (
    SubscriptionCreate,
    PaymentCreate,
    SubscriptionResponse,
    PaymentResponse,
)

# Configure logging
logger = logging.getLogger(__name__)


class RabbitMQService:
    def __init__(self):
        self.connection = None
        self.channel = None
        self.queue_name = "billing_queue"
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
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            raise

    def publish_message(self, message_type: str, data: dict) -> bool:
        """Publish a message to the queue"""
        try:
            if not self.connection or self.connection.is_closed:
                self.connect()

            message = {"type": message_type, **data}

            self.channel.basic_publish(
                exchange="",
                routing_key=self.queue_name,
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


class BillingService:
    @staticmethod
    def create_subscription(
        subscription_data: SubscriptionCreate,
    ) -> SubscriptionResponse:
        """Create a new subscription"""
        db = db_session()
        try:
            subscription = SubscriptionModel(
                user_email=subscription_data.user_email,
                plan_type=subscription_data.plan_type,
                end_date=subscription_data.end_date,
                status=SubscriptionStatus.PENDING,
            )
            db.add(subscription)
            db.commit()
            db.refresh(subscription)
            return SubscriptionResponse.model_validate(subscription)
        finally:
            db.close()

    @staticmethod
    def process_payment(
        subscription_id: int, payment_data: PaymentCreate
    ) -> PaymentResponse:
        """Process a payment for a subscription"""
        db = db_session()
        try:
            # Mock payment processing
            transaction_id = str(uuid.uuid4())

            payment = PaymentModel(
                subscription_id=subscription_id,
                amount=payment_data.amount,
                currency=payment_data.currency,
                payment_method=payment_data.payment_method,
                status="completed",  # Mock successful payment
                transaction_id=transaction_id,
            )

            # Update subscription status
            subscription = (
                db.query(SubscriptionModel)
                .filter(SubscriptionModel.id == subscription_id)
                .first()
            )
            if subscription:
                subscription.status = SubscriptionStatus.ACTIVE
                # Publish subscription activated message
                rabbitmq_service.publish_message(
                    "subscription_activated",
                    {
                        "subscription_id": subscription.id,
                        "user_email": subscription.user_email,
                        "end_date": subscription.end_date.isoformat(),
                    },
                )

            db.add(payment)
            db.commit()
            db.refresh(payment)
            return PaymentResponse.model_validate(payment)
        finally:
            db.close()

    @staticmethod
    def get_subscription(subscription_id: int) -> Optional[SubscriptionResponse]:
        """Get subscription by ID"""
        db = db_session()
        try:
            subscription = (
                db.query(SubscriptionModel)
                .filter(SubscriptionModel.id == subscription_id)
                .first()
            )
            return (
                SubscriptionResponse.model_validate(subscription)
                if subscription
                else None
            )
        finally:
            db.close()

    @staticmethod
    def get_user_subscriptions(user_email: str) -> List[SubscriptionResponse]:
        """Get all subscriptions for a user"""
        db = db_session()
        try:
            subscriptions = (
                db.query(SubscriptionModel)
                .filter(SubscriptionModel.user_email == user_email)
                .all()
            )
            return [SubscriptionResponse.model_validate(sub) for sub in subscriptions]
        finally:
            db.close()

    @staticmethod
    def cancel_subscription(subscription_id: int) -> Optional[SubscriptionResponse]:
        """Cancel a subscription
        Users can cancel their subscription through the /subscriptions/{id}/cancel endpoint
        The billing service updates the subscription status to CANCELLED
        The next time the user requests a workout, they'll get the basic plan with 6 exercises
        """
        db = db_session()
        try:
            subscription = (
                db.query(SubscriptionModel)
                .filter(SubscriptionModel.id == subscription_id)
                .first()
            )
            if subscription:
                subscription.status = SubscriptionStatus.CANCELLED
                db.commit()
                db.refresh(subscription)

                # Publish subscription cancelled message
                rabbitmq_service.publish_message(
                    "subscription_cancelled",
                    {
                        "subscription_id": subscription.id,
                        "user_email": subscription.user_email,
                    },
                )

                return SubscriptionResponse.model_validate(subscription)
            return None
        finally:
            db.close()

    @staticmethod
    def check_expiring_subscriptions(days: int = 7) -> List[SubscriptionResponse]:
        """Check for subscriptions that will expire in the next X days"""
        db = db_session()
        try:
            today = datetime.utcnow()
            end_date = today + timedelta(days=days)

            expiring_subs = (
                db.query(SubscriptionModel)
                .filter(
                    SubscriptionModel.status == SubscriptionStatus.ACTIVE,
                    SubscriptionModel.end_date <= end_date,
                    SubscriptionModel.end_date > today,
                )
                .all()
            )

            # Publish expiring subscriptions message
            for sub in expiring_subs:
                rabbitmq_service.publish_message(
                    "subscription_expiring",
                    {
                        "subscription_id": sub.id,
                        "user_email": sub.user_email,
                        "days_until_expiry": (sub.end_date - today).days,
                    },
                )

            return [SubscriptionResponse.model_validate(sub) for sub in expiring_subs]
        finally:
            db.close()
