from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import os
from pydantic import ValidationError
from models_dto import UserSchema, LoginSchema
from services.user_service import create_user, authenticate_user

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "default-secret")
app.config["JWT_HEADER_NAME"] = os.getenv("JWT_HEADER_NAME", "Authorization")
app.config["JWT_HEADER_TYPE"] = os.getenv("JWT_HEADER_TYPE", "Bearer")
app.config["JWT_TOKEN_LOCATION"] = ["headers"]

jwt = JWTManager(app)

@app.route("/health")
def health():
    return {"status": "UP"}

@app.route("/users", methods=["POST"])
def create_user_route():
    try:
        user_data = request.get_json()
        user = UserSchema.model_validate(user_data)
        created_user = create_user(user)
        return jsonify(created_user.model_dump()), 201
    except ValidationError as e:
        return jsonify({"error": "Invalid user data", "details": e.errors()}), 400
    except Exception as e:
        return jsonify({"error": "Error creating user", "details": str(e)}), 500

@app.route("/oauth/token", methods=["POST"])
def login():
    try:
        login_data = request.get_json()
        login_schema = LoginSchema.model_validate(login_data)
        
        user = authenticate_user(login_schema.email, login_schema.password)
        if not user:
            return jsonify({"error": "Invalid credentials"}), 401
        
        access_token = create_access_token(identity=user.email)
        return jsonify({"access_token": access_token, "token_type": "bearer"}), 200
    except ValidationError as e:
        return jsonify({"error": "Invalid login data", "details": e.errors()}), 400
    except Exception as e:
        return jsonify({"error": "Error logging in", "details": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True) 