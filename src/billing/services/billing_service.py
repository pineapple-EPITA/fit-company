from datetime import datetime, timedelta
import uuid
import json
import logging
from typing import Optional, List
from ..database import db_session
from ..models_db import SubscriptionModel, PaymentModel, SubscriptionStatus, PlanType
from ..models_dto import (
    SubscriptionCreate,
    PaymentCreate,
    SubscriptionResponse,
    PaymentResponse,
)
from .rabbitmq_service import rabbitmq_service

# Configure logging
logger = logging.getLogger(__name__)


class BillingService:
    @staticmethod
    def create_subscription(
        subscription_data: SubscriptionCreate,
    ) -> SubscriptionResponse:
        """Create a new subscription"""
        db = db_session()
        try:
            # Convert plan_type string to enum
            plan_type = PlanType(subscription_data.plan_type.lower())

            # Check for existing active subscription of the same plan type
            existing = (
                db.query(SubscriptionModel)
                .filter(
                    SubscriptionModel.user_email == subscription_data.user_email,
                    SubscriptionModel.plan_type == plan_type,
                    SubscriptionModel.status == SubscriptionStatus.ACTIVE
                )
                .first()
            )
            if existing:
                raise Exception(f"User already has an active subscription for the {plan_type.value} plan.")

            subscription = SubscriptionModel(
                user_email=subscription_data.user_email,
                user_id=subscription_data.user_id or 0,  # Default to 0 if not provided
                plan_type=plan_type,
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
