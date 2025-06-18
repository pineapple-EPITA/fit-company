from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Float
from sqlalchemy.orm import relationship
from .database import Base


class ExercisePerformed(Base):
    __tablename__ = "performed_exercises"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    actual_reps = Column(Integer, nullable=True)
    actual_weight = Column(Float, nullable=True)
    performed_at = Column(DateTime, nullable=False)
    calories_burned = Column(Float, nullable=True)

    workout_id = Column(Integer, ForeignKey("workout_stats.id"))
    workouts = relationship("WorkoutStats", back_populates="exercises")

    def __repr__(self):
        return f"<ExercisePerformed(id={self.id}, name='{self.name}', actual_reps={self.actual_reps}, actual_weight={self.actual_weight}, performed_at='{self.performed_at}')>"

class WorkoutStats(Base):
    __tablename__ = "workout_stats"
    
    id = Column(Integer, primary_key=True, index=True)
    generated_at = Column(DateTime, nullable=False)
    user_email = Column(String, nullable=False, index=True)
    fitness_goal = Column(String, nullable=True)

    exercises = relationship("ExercisePerformed", back_populates="workouts")
    def __repr__(self):
        return f"<WorkoutStats(id={self.id}, user_email='{self.user_email}', generated_at='{self.generated_at}', fitness_goal='{self.fitness_goal}')>"
    