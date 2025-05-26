from models.models_dto import Exercise, WODRequest, WODResponse
import random
from typing import List, Dict

class WODService:
    def __init__(self):
        # Exercise database - in a real service, this would come from a database
        self.exercises = {
            "beginner": [
                {"name": "Push-ups", "sets": 3, "reps": 10},
                {"name": "Squats", "sets": 3, "reps": 15},
                {"name": "Plank", "sets": 3, "duration": 30},
            ],
            "intermediate": [
                {"name": "Burpees", "sets": 4, "reps": 12},
                {"name": "Pull-ups", "sets": 4, "reps": 8},
                {"name": "Mountain Climbers", "sets": 4, "duration": 45},
            ],
            "advanced": [
                {"name": "Muscle-ups", "sets": 5, "reps": 6},
                {"name": "Handstand Push-ups", "sets": 5, "reps": 8},
                {"name": "Box Jumps", "sets": 5, "reps": 15},
            ]
        }

    def generate_wod(self, request: WODRequest) -> WODResponse:
        """
        Generate a Workout of the Day (WOD) based on user's fitness level and goals
        """
        # Select exercises based on fitness level
        level = request.fitness_level.lower()
        available_exercises = self.exercises.get(level, self.exercises["beginner"])
        
        # Filter exercises based on available equipment
        filtered_exercises = [
            ex for ex in available_exercises 
            if self._is_equipment_available(ex["name"], request.equipment_available)
        ]
        
        # Select 4-6 exercises for the WOD
        num_exercises = random.randint(4, 6)
        selected_exercises = random.sample(filtered_exercises, min(num_exercises, len(filtered_exercises)))
        
        # Convert to Exercise objects
        exercises = [
            Exercise(
                name=ex["name"],
                sets=ex["sets"],
                reps=ex.get("reps", 0),
                duration=ex.get("duration", None)
            )
            for ex in selected_exercises
        ]
        
        # Calculate total duration (rough estimate)
        total_duration = sum(
            ex.sets * (ex.duration or 30)  # Assume 30s per rep if no duration specified
            for ex in exercises
        ) // 60  # Convert to minutes
        
        # Estimate calories burned (very rough estimate)
        calories_burned = total_duration * 10  # Assume 10 calories per minute
        
        return WODResponse(
            exercises=exercises,
            total_duration=total_duration,
            difficulty=level,
            calories_burned=calories_burned
        )
    
    def _is_equipment_available(self, exercise_name: str, available_equipment: List[str]) -> bool:
        """
        Check if the exercise can be performed with available equipment
        """
        # This is a simplified check - in a real service, we'd have a proper mapping
        equipment_required = {
            "Pull-ups": ["pull-up bar"],
            "Muscle-ups": ["pull-up bar", "rings"],
            "Box Jumps": ["box"],
            "Handstand Push-ups": ["wall"],
        }
        
        required = equipment_required.get(exercise_name, [])
        return all(equip in available_equipment for equip in required) 