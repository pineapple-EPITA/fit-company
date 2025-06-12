from .database import Base
from sqlalchemy import Column, String, Integer, DateTime, Float
from datetime import datetime


class WorkoutStat(Base):
    __tablename__ = "workout_stats"

    id = Column(Integer, primary_key=True)
    user_id = Column(String, nullable=False)
    exercise_id = Column(String, nullable=False)
    sets = Column(Integer, nullable=True)
    reps_per_set = Column(Integer, nullable=True)
    weight = Column(Float, nullable=True)
    duration_seconds = Column(Float, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<WorkoutStat(id={self.id}, user_id='{self.user_id}', exercise_id='{self.exercise_id}', sets={self.sets}, reps_per_set={self.reps_per_set}, weight={self.weight})>"
