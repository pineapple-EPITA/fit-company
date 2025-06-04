import os
import requests
from sqlalchemy import text
from .database import engine, SessionLocal
from .models_db import UserModel

def sync_users_from_monolith():
    """Sync users from monolith to coach database."""
    monolith_url = os.getenv("MONOLITH_URL")
    headers = {"Authorization": "Bearer bootstrap-secret-key"}
    
    try:
        response = requests.get(f"{monolith_url}/users", headers=headers)
        response.raise_for_status()
        users = response.json()
        
        db = SessionLocal()
        try:
            for user in users:
                # Check if user already exists
                existing_user = db.query(UserModel).filter(UserModel.email == user["email"]).first()
                if not existing_user:
                    new_user = UserModel(
                        email=user["email"],
                        name=user["name"],
                        role=user["role"],
                        password_hash="dummy_hash", 
                        weight=None,
                        height=None,
                        fitness_goal=None,
                        onboarded="false"
                    )
                    db.add(new_user)
            db.commit()
        finally:
            db.close()
    except Exception as e:
        print(f"Error syncing users: {str(e)}")
        raise e

def init_fitness_data():
    """
    Initialize the fitness database with muscle groups and exercises
    from the SQL script file.
    """
    # Path to the SQL script file
    script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sql_file_path = os.path.join(script_dir, "coach", "db_init_scripts", "init_muscle_groups_exercises.sql")
    
    try:
        # Read the SQL file
        with open(sql_file_path, 'r') as file:
            sql_script = file.read()
        
        # Execute the SQL script using SQLAlchemy
        with engine.connect() as connection:
            connection.execute(text(sql_script))
            connection.commit()
        
        print("Fitness data initialized successfully!")
        sync_users_from_monolith()
        return True
    except Exception as e:
        print(f"Error initializing fitness data: {e}")
        return False

if __name__ == "__main__":
    # This allows the script to be run directly
    init_fitness_data() 