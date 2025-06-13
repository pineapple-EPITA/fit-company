from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class ExercisePerformedDTO(BaseModel):
    name: str
    actual_reps: Optional[int] = None
    actual_weight: Optional[float] = None
    performed_at: datetime


class WorkoutStatsDTO(BaseModel):
    user_email: str
    generated_at: datetime
    exercises: List[ExercisePerformedDTO]
