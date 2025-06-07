from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, Table, Text, DateTime
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime

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
    

class WodModel(Base):
    __tablename__ = "wods"

    id = Column(Integer, primary_key=True, index=True)
    user_email = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    
    # Relationships
    exercises = relationship("WodExerciseModel", back_populates="wod", cascade="all, delete")


    def __repr__(self):
        return f"<Wod(id={self.id}, user_email='{self.user_email}', exercise_id={self.exercise_id})>"
    def serialize(self): # to convert to dict
        return {
            "id": self.id,
            "user_email": self.user_email,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
    
class WodExerciseModel(Base):
    __tablename__ = "wod_exercises"
    
    id = Column(Integer, primary_key=True)
    wod_id = Column(Integer, ForeignKey("wods.id", ondelete="CASCADE"))
    exercise_id = Column(Integer, ForeignKey("exercises.id"))
    
    wod = relationship("WodModel", back_populates="exercises")
    exercise = relationship("ExerciseModel")
    
    def serialize(self):
        return {
            "id": self.id,
            "exercise_id": self.exercise_id,
            "exercise_name": self.exercise.name if self.exercise else None
        }

