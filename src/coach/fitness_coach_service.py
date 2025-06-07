import os
from typing import List, Tuple
from sqlalchemy.orm import joinedload

import requests
from .models_db import ExerciseModel, MuscleGroupModel, exercise_muscle_groups, WodModel, WodExerciseModel
from .database import db_session
import random
from time import time
from datetime import datetime

def heavy_computation(duration_seconds: int = 3):
    """
    Perform CPU-intensive calculations to simulate heavy processing.
    Uses matrix operations which are CPU-intensive.
    """
    start_time = time()
    i = 0
    while (time() - start_time) < duration_seconds:
        j = 0
        while j < 1000000:
            j += 1
        i += 1

def calculate_intensity(difficulty: int) -> float:
    """
    Calculate the intensity of an exercise based on its difficulty level (1-5).
    Returns a value between 0.0 and 1.0.
    """
    # Convert difficulty (1-5) to intensity (0.0-1.0)
    return (difficulty - 1) / 4.0

def get_last_workout_exercises(user_email: str) -> List[int]:
    """
    Get the last workout exercises for a user from the monolith.
    """
    monolith_url = os.getenv("MONOLITH_URL")
    headers = {"X-API-Key": os.getenv("FIT_API_KEY")}
    history_response = requests.post(f"{monolith_url}/workouts/last", headers=headers, json={"email": user_email})
    history_response.raise_for_status()
    history_exercises = history_response.json()

    return [history_exercise["id"] for history_exercise in history_exercises]

def save_workout_exercises(user_email: str, exercise_ids: List[int]):
    """
    Save the workout exercises for a user to the monolith.
    """
    monolith_url = os.getenv("MONOLITH_URL")
    headers = {"X-API-Key": os.getenv("FIT_API_KEY")}
    requests.post(f"{monolith_url}/workouts/register", headers=headers, json={"email": user_email, "exercises": exercise_ids})


def request_wod(user_email: str) -> List[Tuple[ExerciseModel, List[Tuple[MuscleGroupModel, bool]]]]:
    """
    Request a workout of the day (WOD).
    Returns a list of tuples containing:
    - The exercise
    - A list of tuples containing:
      - The muscle group
      - Whether it's a primary muscle group
    
    Avoids repeating exercises from the user's last workout.
    """
    # Simulate heavy computation (AI model processing, complex calculations, etc.) for 1-5 seconds
    heavy_computation(random.randint(1, 5)) # DO NOT REMOVE THIS LINE
    
    db = db_session()
    
    # simulate a random failure for testing retries
    if random.random() < 0.3:
        raise Exception("Random failure for testing retries")
    
    try:
        print(f"[WOD Service] Generating WOD for {user_email}")
        last_exercise_ids = get_last_workout_exercises(user_email)

        available_exercises = db.query(ExerciseModel).filter(
            ~ExerciseModel.id.in_(last_exercise_ids)
        ).all()

        # If we don't have enough exercises (excluding last workout's), include all exercises
        if len(available_exercises) < 6:
            available_exercises = db.query(ExerciseModel).all()
        
        # Select 6 random exercises
        selected_exercises = random.sample(available_exercises, 6) if len(available_exercises) >= 6 else available_exercises
        
        # Store today's exercises in history
        save_workout_exercises(user_email, [exercise.id for exercise in selected_exercises])
        
        # Save generated wod in the db
        wod = WodModel(
            user_email=user_email, 
            created_at=datetime.now(),
            exercises=[WodExerciseModel(exercise_id=ex.id) for ex in selected_exercises])
        try:
            db.add(wod)
            db.commit()
        except Exception as e:
            db.rollback()
            raise

        # For each exercise, get its muscle groups and whether they are primary
        result = []
        for exercise in selected_exercises:
            # Get the junction table information for this exercise
            stmt = db.query(
                MuscleGroupModel,
                exercise_muscle_groups.c.is_primary
            ).join(
                exercise_muscle_groups,
                MuscleGroupModel.id == exercise_muscle_groups.c.muscle_group_id
            ).filter(
                exercise_muscle_groups.c.exercise_id == exercise.id
            )
            
            muscle_groups = [(mg, is_primary) for mg, is_primary in stmt.all()]
            result.append((exercise, muscle_groups))
        return result
    finally:
        db.close()
    
def get_latest_wod(user_email: str) -> WodModel:
    """
    Get the latest WOD for a user.
    """
    db = db_session()
    try:
        wod = (
            db.query(WodModel)
            .filter(WodModel.user_email == user_email)
            .order_by(WodModel.created_at.desc())
            .options(
                joinedload(WodModel.exercises).joinedload(WodExerciseModel.exercise)
            )
            .first()
        )
        return wod
    finally:
        db.close()