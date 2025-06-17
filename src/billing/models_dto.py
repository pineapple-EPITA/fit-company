from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from .models_db import SubscriptionStatus, PlanType

class PaymentBase(BaseModel):
    amount: float = Field(..., gt=0)
    currency: str = Field(default="EUR", min_length=3, max_length=3)
    payment_method: str

class PaymentCreate(PaymentBase):
    pass

class PaymentResponse(PaymentBase):
    id: int
    subscription_id: int
    status: str
    transaction_id: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class SubscriptionBase(BaseModel):
    user_email: str
    plan_type: PlanType
    end_date: datetime

class SubscriptionCreate(SubscriptionBase):
    pass

class SubscriptionResponse(SubscriptionBase):
    id: int
    status: SubscriptionStatus
    start_date: datetime
    created_at: datetime
    updated_at: datetime
    payments: List[PaymentResponse]

    class Config:
        from_attributes = True
        json_encoders = {
            PlanType: lambda v: v.value,
            SubscriptionStatus: lambda v: v.value
        }

class SubscriptionUpdate(BaseModel):
    status: Optional[SubscriptionStatus] = None
    end_date: Optional[datetime] = None 