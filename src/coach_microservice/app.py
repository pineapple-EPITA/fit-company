from flask import Flask, jsonify, g
from flask_jwt_extended import JWTManager, jwt_required
from services.wod_service import request_wod, calculate_intensity
from datetime import datetime
from schema.dto import WodResponseSchema, WodExerciseSchema, MuscleGroupImpact
import random

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'your-secret-key'  # In production, use environment variable

jwt = JWTManager(app)

# Coach service exposes API to generate WODs
@app.route("/fitness/wod", methods=["GET"])
@jwt_required()
def get_wod():
    try:
        user_email = g.user_email 

        exercises_with_muscles = request_wod(user_email)
        print(f"get_wod: Received {len(exercises_with_muscles)} exercises")

        wod_exercises = []
        for exercise in exercises_with_muscles:
            muscle_groups = exercise.get("muscle_groups", []) 

            muscle_impacts = []
            for mg in muscle_groups:
                muscle_impacts.append(
                    MuscleGroupImpact(
                        id=mg["id"],
                        name=mg["name"],
                        body_part=mg["body_part"],
                        is_primary=mg["is_primary"],
                        intensity=calculate_intensity(exercise["difficulty"]) * (1.2 if mg["is_primary"] else 0.8)
                    )
                )


            wod_exercise = WodExerciseSchema(
                id=exercise["id"],
                name=exercise["name"],
                description=exercise["description"],
                difficulty=exercise["difficulty"],
                muscle_groups=muscle_impacts,
                suggested_weight=random.uniform(5.0, 50.0),
                suggested_reps=random.randint(8, 15)
            )

            wod_exercises.append(wod_exercise)

        response = WodResponseSchema(
            exercises=wod_exercises,
            generated_at=datetime.now().isoformat()
        )

        return jsonify(response.model_dump()), 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            "error": "Error generating workout of the day",
            "details": str(e)
        }), 500
        
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5003)