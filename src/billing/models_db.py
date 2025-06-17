from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from .database import Base

class SubscriptionStatus(enum.Enum):
    ACTIVE = "active"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    PENDING = "pending"

class PlanType(enum.Enum):
    BASIC = "basic"
    PREMIUM = "premium"

class SubscriptionModel(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False, index=True)
    plan_type = Column(Enum(PlanType), nullable=False)  # Using the PlanType enum: "basic" or "premium"
    status = Column(Enum(SubscriptionStatus), nullable=False, default=SubscriptionStatus.PENDING)
    start_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    end_date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    payments = relationship("PaymentModel", back_populates="subscription")

class PaymentModel(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True)
    subscription_id = Column(Integer, ForeignKey("subscriptions.id"), nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String(3), nullable=False, default="EUR")
    status = Column(String(20), nullable=False)  # e.g., "completed", "failed", "pending"
    payment_method = Column(String(50), nullable=False)  # e.g., "credit_card", "paypal"
    transaction_id = Column(String(100), unique=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    subscription = relationship("SubscriptionModel", back_populates="payments") 