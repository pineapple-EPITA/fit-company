from pydantic import BaseModel
from typing import List, Optional

class Exercise(BaseModel):
    name: str
    sets: int
    reps: int
    weight: Optional[float] = None
    duration: Optional[int] = None  # in seconds

class WODRequest(BaseModel):
    user_id: str
    fitness_level: str
    goals: List[str]
    equipment_available: List[str]

class WODResponse(BaseModel):
    exercises: List[Exercise]
    total_duration: int  # in minutes
    difficulty: str
    calories_burned: Optional[int] = None 