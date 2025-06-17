from datetime import datetime, timedelta
import uuid
from typing import Optional, List
from ..database import db_session
from ..models_db import SubscriptionModel, PaymentModel, SubscriptionStatus
from ..models_dto import SubscriptionCreate, PaymentCreate, SubscriptionResponse, PaymentResponse

class BillingService:
    @staticmethod
    def create_subscription(subscription_data: SubscriptionCreate) -> SubscriptionResponse:
        """Create a new subscription"""
        db = db_session()
        try:
            subscription = SubscriptionModel(
                user_id=subscription_data.user_id,
                plan_type=subscription_data.plan_type,
                end_date=subscription_data.end_date,
                status=SubscriptionStatus.PENDING
            )
            db.add(subscription)
            db.commit()
            db.refresh(subscription)
            return SubscriptionResponse.model_validate(subscription)
        finally:
            db.close()

    @staticmethod
    def process_payment(subscription_id: int, payment_data: PaymentCreate) -> PaymentResponse:
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
                transaction_id=transaction_id
            )
            
            # Update subscription status
            subscription = db.query(SubscriptionModel).filter(SubscriptionModel.id == subscription_id).first()
            if subscription:
                subscription.status = SubscriptionStatus.ACTIVE
            
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
            subscription = db.query(SubscriptionModel).filter(SubscriptionModel.id == subscription_id).first()
            return SubscriptionResponse.model_validate(subscription) if subscription else None
        finally:
            db.close()

    @staticmethod
    def get_user_subscriptions(user_id: int) -> List[SubscriptionResponse]:
        """Get all subscriptions for a user"""
        db = db_session()
        try:
            subscriptions = db.query(SubscriptionModel).filter(SubscriptionModel.user_id == user_id).all()
            return [SubscriptionResponse.model_validate(sub) for sub in subscriptions]
        finally:
            db.close()

    @staticmethod
    def cancel_subscription(subscription_id: int) -> Optional[SubscriptionResponse]:
        """Cancel a subscription"""
        db = db_session()
        try:
            subscription = db.query(SubscriptionModel).filter(SubscriptionModel.id == subscription_id).first()
            if subscription:
                subscription.status = SubscriptionStatus.CANCELLED
                db.commit()
                db.refresh(subscription)
                return SubscriptionResponse.model_validate(subscription)
            return None
        finally:
            db.close()

    @staticmethod
    def check_expiring_subscriptions(days_threshold: int = 7) -> List[SubscriptionResponse]:
        """Get subscriptions that are about to expire"""
        db = db_session()
        try:
            threshold_date = datetime.utcnow() + timedelta(days=days_threshold)
            subscriptions = db.query(SubscriptionModel).filter(
                SubscriptionModel.status == SubscriptionStatus.ACTIVE,
                SubscriptionModel.end_date <= threshold_date
            ).all()
            return [SubscriptionResponse.model_validate(sub) for sub in subscriptions]
        finally:
            db.close() 