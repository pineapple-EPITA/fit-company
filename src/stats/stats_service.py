import logging
import os
import random
import datetime
import requests
from typing import Optional, List

from .models_db import ExercisePerformed, WorkoutStats
from .models_dto import WorkoutStatsSchema, ExercisePerformedSchema
from .database import db_session

logger = logging.getLogger(__name__)

monolith_url = os.getenv("MONOLITH_URL")
coach_url = os.getenv("COACH_URL")
headers = {"X-API-Key": os.getenv("FIT_API_KEY")}

def calculate_calories(weight: float, reps: int) -> float:
    """
    Calculate calories burned based on weight and reps.
    This is a simplified formula for demonstration purposes.
    """
    # Assuming 0.1 calories burned per kg per rep
    
    if weight is None or reps is None:
        return None
    return round(weight * reps * 0.1, 2)

def get_user_profile(user_email: str) -> Optional[dict]:
    """
    Fetches the user profile from the monolith service.
    
    Returns a dictionary with user profile data or None if not found.
    """
    try:
        response = requests.post(f"{monolith_url}/profile_open", headers=headers, json={"email": user_email})
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Error fetching user profile for {user_email}: {str(e)}")
        return None


def generate_workout_stats(user_email: str) -> Optional[WorkoutStatsSchema]:
    """
    Fetches the last workout exercise list for the given user,
    creates a new WorkoutStats record, and stores performed exercises.

    Returns a WorkoutStatsSchema object or None on error.
    """

    db = db_session()
    try:
        # get last performed exercise IDs from monolith
        resp = requests.post(f"{monolith_url}/workouts/last", headers=headers, json={"email": user_email})
        resp.raise_for_status()
        exercise_ids = resp.json()
        user_data = get_user_profile(user_email)

        if not exercise_ids:
            logger.info(f"No last workout found for user {user_email}")
            return None
        
        if not user_data:
            logger.error(f"User profile not found for {user_email}")
            return None

        # create WorkoutStats record
        workout_stats = WorkoutStats(
            generated_at=datetime.datetime.now(datetime.timezone.utc),
            user_email=user_email,
            fitness_goal=user_data["fitness_goal"],
            
        )
        db.add(workout_stats)
        db.flush() 

        # fetch exercise details from coach + save performed exercises
        exercise_schemas = []
        for ex_id in exercise_ids:
            ex_resp = requests.get(f"{coach_url}/exercises/{ex_id}")
            ex_resp.raise_for_status()
            ex_data = ex_resp.json()
            
            actual_r = random.randint(8, 15)
            actual_w = round(random.uniform(5.0, 50.0), 1)

            performed = ExercisePerformed(
                name=ex_data["name"],
                actual_reps=actual_r,
                actual_weight=actual_w,
                performed_at=datetime.datetime.utcnow(),
                workout_id=workout_stats.id,
                calories_burned=calculate_calories(actual_w, actual_r)
            )
            db.add(performed)
            exercise_schemas.append(performed)

        db.commit()
        logger.info(f"Workout stats generated for user {user_email}")

        return WorkoutStatsSchema(
            id=workout_stats.id,
            generated_at=workout_stats.generated_at.isoformat(),
            user_email=user_email,
            fitness_goal=workout_stats.fitness_goal,
            exercises=[
                ExercisePerformedSchema(
                    id=ex.id,
                    name=ex.name,
                    actual_reps=ex.actual_reps,
                    actual_weight=ex.actual_weight,
                    performed_at=ex.performed_at.isoformat()
                ) for ex in exercise_schemas
            ]
        )

    except requests.RequestException as e:
        logger.error(f"Request error while generating stats for {user_email}: {str(e)}")
        db.rollback()
        return None

    except Exception as e:
        logger.error(f"Unexpected error for {user_email}: {str(e)}")
        db.rollback()
        return None

    finally:
        db.close()

def get_stats_by_user(user_email: str) -> List[WorkoutStatsSchema]:
    db = db_session()
    try:
        stats = (
            db.query(WorkoutStats)
            .filter(WorkoutStats.user_email == user_email)
            .order_by(WorkoutStats.generated_at.desc())
            .all()
        )
        return [
            WorkoutStatsSchema(
                id=w.id,
                generated_at=w.generated_at.isoformat(),
                user_email=w.user_email,
                fitness_goal=w.fitness_goal,
                total_calories_burned=sum(e.calories_burned for e in w.exercises),
                exercises=[
                    ExercisePerformedSchema(
                        id=e.id,
                        name=e.name,
                        actual_reps=e.actual_reps,
                        actual_weight=e.actual_weight,
                        performed_at=e.performed_at.isoformat(),
                        calories_burned=e.calories_burned
                    ) for e in w.exercises
                ]
            ) for w in stats
        ]
    finally:
        db.close()
        
def calculate_total_calories_burned(user_email: str):
    db = db_session()
    try:
        stats = (
            db.query(WorkoutStats)
            .filter(WorkoutStats.user_email == user_email)
            .all()
        )
        total_calories = sum(
            sum(e.calories_burned for e in w.exercises) for w in stats
        )
        return total_calories
    finally:
        db.close()
        
        
def calculate_total_performed_exercises(user_email: str):
    """
    Calculate the total number of performed exercises for a user.
    """
    db = db_session()
    try:
        stats = (
            db.query(WorkoutStats)
            .filter(WorkoutStats.user_email == user_email)
            .all()
        )
        total_exercises = sum(len(w.exercises) for w in stats)
        return total_exercises
    finally:
        db.close()
        
        
def check_milestone(user_email: str):
    """
    Check if the user has reached a milestone of 1000 calories burned.
    If so, return a congratulatory message.
    """
    user_data = get_user_profile(user_email)
    name = user_data["name"]
    total_calories = calculate_total_calories_burned(user_email)
    total_exercises = calculate_total_performed_exercises(user_email)
    
    # calories milestone
    if total_calories >= 1000:
        return f"Congratulations {name}! You've burned {total_calories} calories, road to 5000!"
    elif total_calories >= 5000:
        return f"Awesome work {name}! You've burned {total_calories} calories, keep pushing!"
    elif total_calories >= 10000:
        return f"OMG {name}! You've burned {total_calories} calories, you are god now!"
    
    # exercises milestone
    if total_exercises >= 100:
        return f"Great job {name}! You've performed {total_exercises} exercises, keep it up!"
    elif total_exercises >= 500:
        return f"Wow {name}! You've performed {total_exercises} exercises, you're a machine!"
    return None
        


