import datetime
import random
from .consumer import start_consumer
from flask import Flask, request, jsonify
from pydantic import ValidationError
import requests
import os
import logging
import threading


from .models_dto import MuscleGroupImpact, WodExerciseSchema, WodResponseSchema

from .fitness_coach_service import calculate_intensity, request_wod, get_latest_wod

from .fitness_service import get_exercises_by_muscle_group, get_all_exercises, get_exercise_by_id

from .database import init_db
from .fitness_data_init import init_fitness_data

# Configure Flask logging
logging.basicConfig(level=logging.DEBUG)
app = Flask(__name__)
app.logger.setLevel(logging.DEBUG)

# Force stdout to be unbuffered
import sys
sys.stdout.reconfigure(line_buffering=True)

# Validate required environment variables
if not os.getenv("FIT_API_KEY"):
    raise RuntimeError("FIT_API_KEY environment variable must be set")

# Register blueprints

@app.route("/health")
def health():
    return {"status": "UP"}

@app.route("/exercises", methods=["GET"])
def get_exercises():
    try:
        muscle_group_id = request.args.get("muscle_group_id")
        if muscle_group_id:
            # Get exercises for a specific muscle group
            exercises = get_exercises_by_muscle_group(int(muscle_group_id))
        else:
            # Get all exercises
            exercises = get_all_exercises()
        return jsonify([ex.model_dump() for ex in exercises]), 200
    except Exception as e:
        return jsonify({"error": "Error retrieving exercises", "details": str(e)}), 500

@app.route("/exercises/<int:exercise_id>", methods=["GET"])
def get_exercise(exercise_id):
    try:
        exercise = get_exercise_by_id(exercise_id)
        if not exercise:
            return jsonify({"error": "Exercise not found"}), 404
        return jsonify(exercise.model_dump()), 200
    except Exception as e:
        return jsonify({"error": "Error retrieving exercise", "details": str(e)}), 500

@app.route("/createWod", methods=["POST"])
def create_wod():
    user_email = request.json.get("user_email")
    if not user_email:
        return jsonify({"error": "user_email is required"}), 400
        
    try:
        # Fetch user last workout exercises from monolith
        # app.logger.debug(f"History exercises: {history_exercises}")
        exercises_with_muscles = request_wod(user_email)
        wod_exercises = []
        for exercise, muscle_groups in exercises_with_muscles:
            # Create muscle group impact objects
            muscle_impacts = [
                MuscleGroupImpact(
                    id=mg.id,
                    name=mg.name,
                    body_part=mg.body_part,
                    is_primary=is_primary,
                    # Higher intensity for primary muscle groups
                    intensity=calculate_intensity(exercise.difficulty) * (1.2 if is_primary else 0.8)
                )
                for mg, is_primary in muscle_groups
            ]
            
            # Create exercise object
            wod_exercise = WodExerciseSchema(
                id=exercise.id,
                name=exercise.name,
                description=exercise.description,
                difficulty=exercise.difficulty,
                muscle_groups=muscle_impacts,
                suggested_weight=random.uniform(5.0, 50.0),  # Random weight between 5 and 50 kg
                suggested_reps=random.randint(8, 15)  # Random reps between 8 and 15
            )
            wod_exercises.append(wod_exercise)
        
        response = WodResponseSchema(
            exercises=wod_exercises,
            generated_at=datetime.datetime.now(datetime.UTC).isoformat()
        )
        
        return jsonify(response.model_dump()), 200

        
    except requests.RequestException as e:
        return jsonify({"error": f"Failed to fetch user history: {str(e)}"}), 500
    
@app.route("/wod/<user_email>", methods=["GET"])
def get_wod(user_email):
    if not user_email:
        return jsonify({"error": "user_email is required"}), 400
    try:
        wod = get_latest_wod(user_email)
        if not wod:
            return jsonify({"error": "No WOD found for this user"}), 404
                
        exercises = [ex.serialize() for ex in wod.exercises]  
        
        response = {
            "wod_id": wod.id,
            "created_at": wod.created_at.isoformat(),
            "exercises": exercises
        }
        
        return jsonify(response), 200

    except Exception as e:
        return jsonify({"error": "Error retrieving WOD", "details": str(e)}), 500

    

def run_app():
    """Entry point for the application script"""
    # Initialize the database before starting the app
    init_db()

    init_fitness_data()
    
    consumer_thread = threading.Thread(target=start_consumer, daemon=True)
    consumer_thread.start()
    logging.info("Consumer thread started")
    app.run(host="0.0.0.0", port=5000, debug=True)

if __name__ == "__main__":
    run_app()

