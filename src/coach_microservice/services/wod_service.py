import random
import time as pytime
import requests
import os
from dotenv import load_dotenv

load_dotenv()  


MONOLITH_URL = os.getenv("MONOLITH_URL", "http://localhost:5003")


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

# Coach service should request monolith to get yesterday's user's exercices history
def get_yesterday_exercise(user_email:str):
    response = requests.get(f"{MONOLITH_URL}/fitness/exercises/yesterday", params={"email": user_email})
    response.raise_for_status()
    exercises = response.json()  # list dict
    ids = [ex["id"] for ex in exercises]
    return ids

def get_all_exercises():
    response = requests.get(f"{MONOLITH_URL}/fitness/exercises")
    response.raise_for_status()
    return response.json()

def request_wod(user_email: str):
    """
    Call monolith to get exercises and history, then return a filtered WOD.
    """
    heavy_computation(random.randint(1, 5)) 

    yesterday_ex_ids = get_yesterday_exercise(user_email)  
    all_exercises = get_all_exercises()  

    filtered_exercises = [
        ex for ex in all_exercises if ex["id"] not in yesterday_ex_ids
    ]

    # if there are less than 6 exercises after filtering, use all exercises 
    if len(filtered_exercises) < 6:
        filtered_exercises = all_exercises

    # randomly pick 6 exercises from the filtered list
    selected = random.sample(filtered_exercises, 6) if len(filtered_exercises) >= 6 else filtered_exercises

    return selected  
