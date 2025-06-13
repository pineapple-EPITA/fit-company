from flask import Blueprint, jsonify, request
from .models_db import WorkoutStats, ExercisePerformed
from .database import db_session

stats_bp = Blueprint("stats", __name__)

@stats_bp.route("/workout_stats/<int:workout_id>", methods=["GET"])
def get_workout_stats(workout_id):
    db = db_session()
    try:
        workout = db.query(WorkoutStats).filter(WorkoutStats.id == workout_id).first()
        if not workout:
            return jsonify({"error": "WorkoutStats not found"}), 404
        
        exercises = []
        for ex in workout.exercises:
            exercises.append({
                "id": ex.id,
                "name": ex.name,
                "actual_reps": ex.actual_reps,
                "actual_weight": ex.actual_weight,
                "performed_at": ex.performed_at.isoformat() if ex.performed_at else None
            })

        result = {
            "id": workout.id,
            "generated_at": workout.generated_at.isoformat() if workout.generated_at else None,
            "user_email": workout.user_email,
            "exercises": exercises
        }
        return jsonify(result), 200
    finally:
        db.close()
