from flask import Flask
from .database import init_db
from flask_jwt_extended import JWTManager 
from .services.fitness_data_init import init_fitness_data
from .blueprints.user import user_bp
from .blueprints.auth import auth_bp
from .blueprints.profile import profile_bp
from .blueprints.fitness import fitness_bp
from dotenv import load_dotenv
import os

app = Flask(__name__)
load_dotenv()

app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "default-secret")
app.config["JWT_HEADER_NAME"] = os.getenv("JWT_HEADER_NAME", "Authorization")
app.config["JWT_HEADER_TYPE"] = os.getenv("JWT_HEADER_TYPE", "Bearer")
app.config["JWT_TOKEN_LOCATION"] = ["headers"]

jwt = JWTManager(app)

# Register blueprints
app.register_blueprint(user_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(profile_bp)
app.register_blueprint(fitness_bp)

@app.route("/health")
def health():
    return {"status": "UP"}

def run_app():
    """Entry point for the application script"""
    # Initialize the database before starting the app
    init_db()
    
    # Initialize fitness data
    init_fitness_data()
    
    # Get debug mode from environment variable, default to False
    debug_mode = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    app.run(host="0.0.0.0", port=5000, debug=debug_mode)

if __name__ == "__main__":
    run_app()

