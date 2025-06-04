from flask import Blueprint, request, jsonify
from pydantic import ValidationError
from ..models_dto import  RegisterWorkoutSchema
from ..services.workout_service import get_last_workout_exercises, register_workout
from ..services.auth_service import  api_key_required

workout_bp = Blueprint('workout', __name__)


@workout_bp.route("/last", methods=["POST"])
@api_key_required
def get_user_last_workout():
    try:
        email = request.json.get("email")
        if not email:
            return jsonify({"error": "email is required"}), 400
        
        exercises = get_last_workout_exercises(email)
        if exercises is None:
            return jsonify([]), 200
            
        return jsonify([exercise.model_dump() for exercise in exercises]), 200
        
    except Exception as e:
        return jsonify({"error": "Error retrieving last workout", "details": str(e)}), 500 
    
@workout_bp.route("/register", methods=["POST"])
@api_key_required
def perform_workout():
    try:
        workout_data = request.get_json()
        workout = RegisterWorkoutSchema.model_validate(workout_data)
        register_workout(workout.email, workout.exercises)
        return jsonify({"message": "Workout registered successfully"}), 200
        
    except ValidationError as e:
        return jsonify({"error": "Invalid workout data", "details": e.errors()}), 400
    except Exception as e:
        return jsonify({"error": "Error registering workout", "details": str(e)}), 500 
    
    
    