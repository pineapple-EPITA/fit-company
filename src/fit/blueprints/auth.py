from flask import Blueprint, request, jsonify
from pydantic import ValidationError
import datetime
from ..models_dto import LoginSchema, TokenSchema
from ..services.auth_service import authenticate_user, create_access_token
from ..services.user_service import create_user as create_user_service
from ..models_dto import UserSchema
from ..database import db_session
from ..models_db import UserModel
import os

auth_bp = Blueprint('auth', __name__)

BOOTSTRAP_KEY = os.environ.get("BOOTSTRAP_KEY", "bootstrap-secret-key")

@auth_bp.route("/oauth/token", methods=["POST"])
def login():
    try:
        content_type = request.headers.get('Content-Type', '')
        if 'application/x-www-form-urlencoded' in content_type:
            login_data = {
                "email": request.form.get("username"),
                "password": request.form.get("password")
            }
        else:
            login_data = request.get_json()
            
        login_schema = LoginSchema.model_validate(login_data)
        
        user = authenticate_user(login_schema.email, login_schema.password)
        if not user:
            return jsonify({"error": "Invalid credentials"}), 401
        
        access_token_expires = datetime.timedelta(minutes=30)
        token_data = {
            "sub": user.email,
            "name": user.name,
            "role": user.role,
            "iss": "fit-api",
            "iat": datetime.datetime.now(datetime.UTC),
        }
        
        access_token = create_access_token(
            data=token_data,
            expires_delta=access_token_expires
        )
        
        token = TokenSchema(
            access_token=access_token,
            token_type="bearer"
        )
        
        response_data = token.model_dump()
        response_data["onboarded"] = user.onboarded
        
        return jsonify(response_data), 200
        
    except ValidationError as e:
        return jsonify({"error": "Invalid login data", "details": e.errors()}), 400
    except Exception as e:
        return jsonify({"error": "Error logging in", "details": str(e)}), 500

@auth_bp.route("/bootstrap/admin", methods=["POST"])
def create_bootstrap_admin():
    try:
        bootstrap_key = request.headers.get('X-Bootstrap-Key')
        if not bootstrap_key or bootstrap_key != BOOTSTRAP_KEY:
            return jsonify({"error": "Invalid bootstrap key"}), 401
            
        db = db_session()
        admin_exists = db.query(UserModel).filter(UserModel.role == "admin").first() is not None
        db.close()
        
        if admin_exists:
            return jsonify({"error": "Admin user already exists"}), 409
            
        admin_data = request.get_json()
        admin_data["role"] = "admin"
        
        admin_user = UserSchema.model_validate(admin_data)
        created_admin = create_user_service(admin_user)
        
        return jsonify(created_admin.model_dump()), 201
        
    except ValidationError as e:
        return jsonify({"error": "Invalid admin data", "details": e.errors()}), 400
    except Exception as e:
        return jsonify({"error": "Error creating admin", "details": str(e)}), 500 