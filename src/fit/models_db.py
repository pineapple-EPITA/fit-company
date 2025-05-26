from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, Boolean, ForeignKey, Table, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from .database import Base

class UserModel(Base):
    __tablename__ = "users"

    email = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    role = Column(String, nullable=False)
    password_hash = Column(String, nullable=False)
    
    # Profile information (nullable as they'll be filled during onboarding)
    weight = Column(Float, nullable=True)
    height = Column(Float, nullable=True)
    fitness_goal = Column(String, nullable=True)
    onboarded = Column(String, default="false", nullable=False)
    
    exercise_histories = relationship("ExerciseHistoryModel", back_populates="user")
    def __repr__(self):
        return f"<User(email='{self.email}', name='{self.name}', role='{self.role}')>"

# Junction table for the many-to-many relationship between exercises and muscle groups
exercise_muscle_groups = Table(
    "exercise_muscle_groups",
    Base.metadata,
    Column("exercise_id", Integer, ForeignKey("exercises.id", ondelete="CASCADE"), primary_key=True),
    Column("muscle_group_id", Integer, ForeignKey("muscle_groups.id", ondelete="CASCADE"), primary_key=True),
    Column("is_primary", Boolean, default=False, nullable=False),
)

class MuscleGroupModel(Base):
    __tablename__ = "muscle_groups"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    body_part = Column(String(50), nullable=False)
    description = Column(Text)
    
    # Relationship to exercises
    exercises = relationship(
        "ExerciseModel", 
        secondary=exercise_muscle_groups,
        back_populates="muscle_groups"
    )

    def __repr__(self):
        return f"<MuscleGroup(id={self.id}, name='{self.name}', body_part='{self.body_part}')>"

class ExerciseModel(Base):
    __tablename__ = "exercises"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    difficulty = Column(Integer, nullable=False)
    equipment = Column(String(100))
    instructions = Column(Text)
    
    # Relationship to muscle groups
    muscle_groups = relationship(
        "MuscleGroupModel",
        secondary=exercise_muscle_groups,
        back_populates="exercises"
    )

    def __repr__(self):
        return f"<Exercise(id={self.id}, name='{self.name}', difficulty={self.difficulty})>" 
    
class ExerciseHistoryModel(Base):
    __tablename__ = "exercise_history"

    id = Column(Integer, primary_key=True, index=True)
    user_email = Column(String, ForeignKey("users.email"), nullable=False)
    exercise_id = Column(Integer, ForeignKey("exercises.id"), nullable=False)
    performed_at = Column(DateTime, default=datetime, nullable=False)
    duration_minutes = Column(Float, nullable=True)
    reps = Column(Integer, nullable=True)

    user = relationship("UserModel", back_populates="exercise_histories")
    exercise = relationship("ExerciseModel")
    
    def __repr__(self):
        return f"<ExerciseHistory(id={self.id}, user_email='{self.user_email}', exercise_id={self.exercise_id}, performed_at={self.performed_at})>"
