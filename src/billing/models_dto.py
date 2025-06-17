from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional, List
from .models_db import SubscriptionStatus, PlanType

class PaymentBase(BaseModel):
    amount: float = Field(..., gt=0)
    currency: str = Field(default="EUR", min_length=3, max_length=3)
    payment_method: str

    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat(),
            PlanType: lambda v: v.value,
            SubscriptionStatus: lambda v: v.value
        }
    )

class PaymentCreate(PaymentBase):
    pass

class PaymentResponse(PaymentBase):
    id: int
    subscription_id: int
    status: str
    transaction_id: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            datetime: lambda v: v.isoformat(),
            PlanType: lambda v: v.value,
            SubscriptionStatus: lambda v: v.value
        }
    )

class SubscriptionBase(BaseModel):
<<<<<<< HEAD
    user_email: str
    plan_type: PlanType
=======
    user_id: int
    plan_type: str = Field(..., pattern="^(basic|premium)$")
>>>>>>> a1837601b151a674de05520f8ccaf6ebedb62b3d
    end_date: datetime

    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat(),
            PlanType: lambda v: v.value,
            SubscriptionStatus: lambda v: v.value
        }
    )

class SubscriptionCreate(SubscriptionBase):
    pass

class SubscriptionResponse(SubscriptionBase):
    id: int
    status: str
    start_date: datetime
    created_at: datetime
    updated_at: datetime
    payments: List[PaymentResponse]

<<<<<<< HEAD
    class Config:
        from_attributes = True
        json_encoders = {
            PlanType: lambda v: v.value,
            SubscriptionStatus: lambda v: v.value
        }
=======
    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            datetime: lambda v: v.isoformat(),
            PlanType: lambda v: v.value,
            SubscriptionStatus: lambda v: v.value
        }
    )
>>>>>>> a1837601b151a674de05520f8ccaf6ebedb62b3d

class SubscriptionUpdate(BaseModel):
    status: Optional[SubscriptionStatus] = None
    end_date: Optional[datetime] = None

    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat(),
            PlanType: lambda v: v.value,
            SubscriptionStatus: lambda v: v.value
        }
    ) 