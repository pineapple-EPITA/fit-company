from flask import Blueprint, request, jsonify, g
from datetime import datetime
import random
from ..models_dto import WodResponseSchema, WodExerciseSchema, MuscleGroupImpact, ExerciseHistoryCreateSchema, ExerciseHistoryResponseSchema
from ..models_db import ExerciseHistoryModel
from ..services.fitness_service import (
    get_all_exercises, get_exercise_by_id, get_exercises_by_muscle_group, get_exercises_performed_yesterday,
    get_exercises_performed
)
from ..services.fitness_coach_service import calculate_intensity, request_wod
from flask_jwt_extended import jwt_required, get_jwt_identity
from pydantic import ValidationError
from ..database import db_session


fitness_bp = Blueprint('fitness', __name__)

@fitness_bp.route("/fitness/exercises", methods=["GET"])
def get_exercises():
    try:
        muscle_group_id = request.args.get("muscle_group_id")
        if muscle_group_id:
            exercises = get_exercises_by_muscle_group(int(muscle_group_id))
        else:
            exercises = get_all_exercises()
        return jsonify([ex.model_dump() for ex in exercises]), 200
    except Exception as e:
        return jsonify({"error": "Error retrieving exercises", "details": str(e)}), 500

@fitness_bp.route("/fitness/exercises/<int:exercise_id>", methods=["GET"])
def get_exercise(exercise_id):
    try:
        exercise = get_exercise_by_id(exercise_id)
        if not exercise:
            return jsonify({"error": "Exercise not found"}), 404
        return jsonify(exercise.model_dump()), 200
    except Exception as e:
        return jsonify({"error": "Error retrieving exercise", "details": str(e)}), 500

@fitness_bp.route("/fitness/wod", methods=["GET"])
@jwt_required()
def get_wod():
    try:
        user_email = g.user_email

        exercises_with_muscles = request_wod(user_email)
        print(f"get_wod: Received {len(exercises_with_muscles)} exercises")

        wod_exercises = []
        for exercise, muscle_groups in exercises_with_muscles:
            print(f"Processing Exercise ID: {exercise.id}, Name: {exercise.name}")
            muscle_impacts = []
            for mg, is_primary in muscle_groups:
                print(f"Muscle: {mg.name}, Primary: {is_primary}")
                muscle_impacts.append(
                    MuscleGroupImpact(
                        id=mg.id,
                        name=mg.name,
                        body_part=mg.body_part,
                        is_primary=is_primary,
                        intensity=calculate_intensity(exercise.difficulty) * (1.2 if is_primary else 0.8)
                    )
                )

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
            generated_at = datetime.now().isoformat()
        )

        return jsonify(response.model_dump()), 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            "error": "Error generating workout of the day",
            "details": str(e)
        }), 500

@fitness_bp.route("/fitness/exercises/yesterday", methods=["GET"])
@jwt_required()
def get_performed_exercises_yesterday():
    try:
        user_email = g.user_email
        yesterday_exercises = get_exercises_performed_yesterday(user_email)
        
        if not yesterday_exercises:
            return jsonify({"message": "No exercises performed yesterday"}), 200
        
        return jsonify([ex.model_dump() for ex in yesterday_exercises]), 200
        
    except Exception as e:
        return jsonify({"error": "Error retrieving yesterday's exercises", "details": str(e)}), 500
    
@fitness_bp.route("/fitness/exercises/history", methods=["GET"])
@jwt_required()
def get_exercise_history():
    try:
        user_email = g.user_email
        history = get_exercises_performed(user_email)
        
        if not history:
            return jsonify({"message": "No exercise history found"}), 200
        
        return jsonify([entry.model_dump() for entry in history]), 200
        
    except Exception as e:
        return jsonify({"error": "Error retrieving exercise history", "details": str(e)}), 500

@fitness_bp.route("/fitness/exercises/history", methods=["POST"])
@jwt_required()
def add_exercise_history():
    try:
        user_email = g.user_email
        history_data = request.get_json()
        history = ExerciseHistoryCreateSchema.model_validate(history_data)
        
        db = db_session()
        new_history = ExerciseHistoryModel(
            user_email=user_email,
            exercise_id=history.exercise_id,
            performed_at=history.performed_at or datetime.now(),
            duration_minutes=history.duration_minutes,
            reps=history.reps
        )
        db.add(new_history)
        db.commit()
        db.refresh(new_history)
        db.close()
        
        return jsonify(ExerciseHistoryResponseSchema.model_validate(new_history).model_dump()), 201
    except ValidationError as e:
        return jsonify({"error": "Invalid exercise history data", "details": e.errors()}), 400
    except Exception as e:
        return jsonify({"error": "Error adding exercise history", "details": str(e)}), 500