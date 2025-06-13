import logging
import os
from typing import List, Tuple
from .models_db import ExercisePerformed, WorkoutStats
from .models_dto import WorkoutStatsSchema, ExercisePerformedSchema
from .database import db_session
import random
from time import time
import requests
import datetime
from flask import Flask, request, jsonify


logger = logging.getLogger(__name__)

monolith_url = os.getenv("MONOLITH_URL")
coach_url = os.getenv("COACH_URL")
headers = {"X-API-Key": os.getenv("FIT_API_KEY")}


def generate_workout_stats(user_email: str):
    """
    Generates workout statistics for a user by fetching their last performed exercises
    from a monolith service and storing the data in the database.

    """
    
    db = db_session()
    
    try:
        # fetch last performed exercises from monolith
        response = requests.post(f"{monolith_url}/workouts/last", headers=headers, json={"email": user_email})
        response.raise_for_status()
        exercise_ids = response.json()

        if not exercise_ids:
            logger.info(f"No last workout exercises found for user {user_email}")
            return None

        # create WorkoutStats entry
        workout_stats = WorkoutStats(
            generated_at=datetime.datetime.now(datetime.UTC).isoformat(),
            user_email=user_email
        )
        db.add(workout_stats)
        db.flush()  # flush to get the ID

        # create ExercisePerformed entries
        for exercise_id in exercise_ids:
            detail_resp = requests.get(f"{coach_url}/exercises/{exercise_id}")
            detail_resp.raise_for_status()
            detail = detail_resp.json()
            
            performed_exercise = ExercisePerformed(
                name=detail['name'],
                actual_reps=random.randint(8, 15), # for example, random reps between 8 and 15
                actual_weight=round(random.uniform(5.0, 50.0), 1), # for example, random weight between 5 and 50 kg
                performed_at=datetime.utcnow(),
                workout_id=workout_stats.id
            )
            db.add(performed_exercise)

        db.commit()
        logger.info(f"Workout stats generated for user {user_email}")

        # Return the generated workout stats
        response = WorkoutStatsSchema(
            id=workout_stats.id,
            generated_at=workout_stats.generated_at,
            user_email=workout_stats.user_email,
            exercises=[ExercisePerformedSchema(
                id=exercise.id,
                name=exercise.name,
                actual_reps=exercise.actual_reps,
                actual_weight=exercise.actual_weight,
                performed_at=exercise.performed_at.isoformat()
            ) for exercise in workout_stats.exercises]
        )
        return jsonify(response.model_dump()), 200

    except requests.RequestException as e:
        logger.error(f"HTTP error for user {user_email}: {str(e)}")
        db.rollback()
        return None

    except Exception as e:
        logger.error(f"Internal error for user {user_email}: {str(e)}")
        db.rollback()
        return None

    finally:
        db.close()
    

