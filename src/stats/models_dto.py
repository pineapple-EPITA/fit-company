from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime


class StatsCreateRequest(BaseModel):
    user_id: str
    exercise_id: str
    sets: Optional[int] = Field(None, ge=1)
    reps_per_set: Optional[int] = Field(None, ge=1)
    weight: Optional[float] = Field(None, ge=0)
    duration_seconds: Optional[float] = Field(None, ge=0)

    @field_validator("sets", "reps_per_set", "weight", "duration_seconds", pre=True)
    def none_if_blank(cls, v):
        return None if v in ("", None) else v


class StatsResponse(StatsCreateRequest):
    id: str 
    timestamp: datetime = Field(default_factory=datetime.utcnow)
