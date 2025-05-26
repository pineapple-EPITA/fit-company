from typing import List, Tuple
from ..models_db import ExerciseModel, MuscleGroupModel, exercise_muscle_groups, ExerciseHistoryModel
from ..database import db_session
import random
from datetime import datetime, timedelta, time
import time as pytime

def heavy_computation(duration_seconds: int = 3):
    """
    Perform CPU-intensive calculations to simulate heavy processing.
    Uses matrix operations which are CPU-intensive.
    """
    start_time = pytime.time()
    i = 0
    while (pytime.time() - start_time) < duration_seconds:
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


def request_wod(user_email: str) -> List[Tuple[ExerciseModel, List[Tuple[MuscleGroupModel, bool]]]]:
    """
    Request a workout of the day (WOD) for a specific user.
    Avoid repeating exercises from the previous day.
    Returns a list of tuples:
    - ExerciseModel instance
    - List of tuples: (MuscleGroupModel, is_primary)
    """
    heavy_computation(random.randint(1, 5)) # DO NOT REMOVE THIS LINE

    db = db_session()
    try:
        # calculate yesterday date range (00:00 to 23:59:59)
        today = datetime.now().date()
        yesterday_date = today - timedelta(days=1)

        yesterday_start = datetime.combine(yesterday_date, time.min) 
        yesterday_end = datetime.combine(yesterday_date, time(23, 59, 59, 999999))

        yesterday_exercise_ids = db.query(ExerciseHistoryModel.exercise_id).filter(
            ExerciseHistoryModel.user_email == user_email,
            ExerciseHistoryModel.performed_at >= yesterday_start,
            ExerciseHistoryModel.performed_at <= yesterday_end
        ).distinct().all()

        yesterday_exercise_ids = [eid for (eid,) in yesterday_exercise_ids]

        # get all exercises excluding those from yesterday
        if yesterday_exercise_ids:
            exercises = db.query(ExerciseModel).filter(~ExerciseModel.id.in_(yesterday_exercise_ids)).all()
        else:
            exercises = db.query(ExerciseModel).all()

        # if not enough exercises remain, fallback to all exercises
        if len(exercises) < 6:
            exercises = db.query(ExerciseModel).all()

        selected_exercises = random.sample(exercises, 6) if len(exercises) >= 6 else exercises

        result = []
        for exercise in selected_exercises:
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
