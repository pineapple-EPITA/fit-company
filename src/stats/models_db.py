from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, Table, DateTime, Float
from sqlalchemy.orm import relationship
from .database import Base

exercise_muscle_groups = Table(
    "exercise_muscle_groups",
    Base.metadata,
    Column("exercise_id", Integer, ForeignKey("performed_exercises.id", ondelete="CASCADE"), primary_key=True),
    Column("muscle_group_id", Integer, ForeignKey("muscle_summary.id", ondelete="CASCADE"), primary_key=True),
    Column("is_primary", Boolean, default=False, nullable=False),
)

class MuscleGroupSummary(Base):
    __tablename__ = "muscle_summary"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    body_part = Column(String(50), nullable=False)
    intensity = Column(Integer, nullable=False)

    exercises = relationship(
        "ExercisePerformed",
        secondary=exercise_muscle_groups,
        back_populates="muscle_groups"
    )

class ExercisePerformed(Base):
    __tablename__ = "performed_exercises"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    actual_reps = Column(Integer, nullable=True)
    actual_weight = Column(Float, nullable=True)
    performed_at = Column(DateTime, nullable=False)

    workout_id = Column(Integer, ForeignKey("workout_stats.id"))
    workout_stats = relationship("WorkoutStats", back_populates="exercises")

    muscle_groups = relationship(
        "MuscleGroupSummary",
        secondary=exercise_muscle_groups,
        back_populates="exercises"
    )

class WorkoutStats(Base):
    __tablename__ = "workout_stats"
    
    id = Column(Integer, primary_key=True, index=True)
    generated_at = Column(DateTime, nullable=False)
    user_email = Column(String, ForeignKey("users.email"))

    user = relationship("StatsUser", back_populates="workouts")
    exercises = relationship("ExercisePerformed", back_populates="workout_stats")

class StatsUser(Base):
    __tablename__ = "users"

    email = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    fitness_goal = Column(String, nullable=True)

    workouts = relationship("WorkoutStats", back_populates="user")
