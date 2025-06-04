import datetime
import random
from flask import Flask, request, jsonify
from pydantic import ValidationError
import requests
import os
import logging
import threading
import json
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from .models_dto import MuscleGroupImpact, WodExerciseSchema, WodResponseSchema
from .models_db import WodModel
from .fitness_coach_service import calculate_intensity, request_wod
from .fitness_service import get_exercises_by_muscle_group, get_all_exercises, get_exercise_by_id
from .database import init_db, SessionLocal, get_db
from .fitness_data_init import init_fitness_data
from .rabbitmq_client import rabbitmq_client

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

WOD_REQUEST_QUEUE = "createWodQueue"
WOD_RESPONSE_QUEUE = "wod_responses"

def process_wod_request(ch, method, properties, body):
    """Process WOD request from the queue"""
    try:
        # 20% random failure
        if random.random() < 0.2:
            raise Exception("Simulated random failure (20%) for testing retries and DLQ.")
        data = json.loads(body)
        user_email = data.get("user_email")
        request_id = data.get("request_id")
        
        exercises_with_muscles = request_wod(user_email)
        wod_exercises = []
        
        for exercise, muscle_groups in exercises_with_muscles:
            muscle_impacts = [
                MuscleGroupImpact(
                    id=mg.id,
                    name=mg.name,
                    body_part=mg.body_part,
                    is_primary=is_primary,
                    intensity=calculate_intensity(exercise.difficulty) * (1.2 if is_primary else 0.8)
                )
                for mg, is_primary in muscle_groups
            ]
            
            wod_exercise = WodExerciseSchema(
                id=exercise.id,
                name=exercise.name,
                description=exercise.description,
                difficulty=exercise.difficulty,
                muscle_groups=muscle_impacts,
                suggested_weight=random.uniform(5.0, 50.0),
                suggested_reps=random.randint(8, 15)
            )
            wod_exercises.append(wod_exercise)
        
        response = WodResponseSchema(
            exercises=wod_exercises,
            generated_at=datetime.datetime.now(datetime.UTC).isoformat()
        )
        
        db = SessionLocal()
        try:
            wod = WodModel(
                user_email=user_email,
                date=datetime.date.today(),
                exercises=response.model_dump()["exercises"],
                generated_at=response.generated_at
            )
            db.add(wod)
            db.commit()
            db.refresh(wod)
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()
        
        ch.basic_ack(delivery_tag=method.delivery_tag)
        
    except Exception as e:
        app.logger.error(f"Error processing WOD request: {str(e)}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

def start_rabbitmq_consumer():
    """Start RabbitMQ consumer in a separate thread"""
    try:
        rabbitmq_client.declare_queue(WOD_REQUEST_QUEUE)
        rabbitmq_client.declare_queue(WOD_RESPONSE_QUEUE)
        rabbitmq_client.consume_messages(WOD_REQUEST_QUEUE, process_wod_request)
    except Exception as e:
        app.logger.error(f"Error starting RabbitMQ consumer: {str(e)}")

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
        request_id = str(datetime.datetime.now(datetime.UTC).timestamp())
        
        rabbitmq_client.publish_message(
            WOD_REQUEST_QUEUE,
            {
                "request_id": request_id,
                "user_email": user_email
            }
        )
        
        return jsonify({
            "request_id": request_id,
            "status": "processing",
            "message": "WOD generation started"
        }), 202
        
    except Exception as e:
        return jsonify({"error": f"Failed to process WOD request: {str(e)}"}), 500

@app.route("/wod/<user_email>", methods=["GET"])
def get_user_wod(user_email):
    """Get the latest WOD for a user"""
    try:
        db = SessionLocal()
        wod = db.query(WodModel).filter(
            WodModel.user_email == user_email,
            WodModel.date == datetime.date.today()
        ).first()
        
        if not wod:
            return jsonify({"error": "No WOD found for today"}), 404
            
        response = WodResponseSchema(
            exercises=wod.exercises,
            generated_at=wod.generated_at
        )
        
        return jsonify(response.model_dump()), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to retrieve WOD: {str(e)}"}), 500
    finally:
        db.close()

def run_app():
    """Entry point for the application script"""
    # Initialize the database before starting the app
    init_db()
    
    if not init_fitness_data():
        app.logger.error("Failed to initialize fitness data and sync users")
        raise RuntimeError("Failed to initialize fitness data and sync users")
    
    consumer_thread = threading.Thread(target=start_rabbitmq_consumer)
    consumer_thread.daemon = True
    consumer_thread.start()
    
    app.run(host="0.0.0.0", port=5000, debug=True)

if __name__ == "__main__":
    run_app()

