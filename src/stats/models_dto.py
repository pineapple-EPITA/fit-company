from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class ExercisePerformedSchema(BaseModel):
    name: str
    actual_reps: Optional[int] = None
    actual_weight: Optional[float] = None
    performed_at: datetime
    calories_burned: Optional[float] = None


class WorkoutStatsSchema(BaseModel):
    user_email: str
    generated_at: datetime
    fitness_goal: Optional[str] = None
    exercises: List[ExercisePerformedSchema]
    total_calories_burned: Optional[float] = None
    


class UserResponse(BaseModel):
    name: str
    user_email: str
    total_workout_performed: Optional[int] = None
    total_calories_burned: Optional[float] = None
    total_performed_exercises: Optional[int] = None
    milestone_achieved: List[dict]
    generated_at: datetime
    