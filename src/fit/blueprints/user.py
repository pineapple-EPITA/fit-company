from flask import Blueprint, request, jsonify, g
from pydantic import ValidationError
from ..models_dto import UserSchema
from ..services.user_service import create_user as create_user_service, get_all_users as get_all_users_service
from ..services.auth_service import admin_required

user_bp = Blueprint('user', __name__)

@user_bp.route("/users", methods=["POST"])
@admin_required
def create_user():
    try:
        user_data = request.get_json()
        user = UserSchema.model_validate(user_data)
        created_user = create_user_service(user)
        return jsonify(created_user.model_dump()), 201
    except ValidationError as e:
        return jsonify({"error": "Invalid user data", "details": e.errors()}), 400
    except Exception as e:
        return jsonify({"error": "Error creating user", "details": str(e)}), 500

@user_bp.route("/users", methods=["GET"])
@admin_required
def get_all_users():
    try:
        users = get_all_users_service()
        return jsonify([user.model_dump() for user in users]), 200
    except Exception as e:
        return jsonify({"error": "Error retrieving users", "details": str(e)}), 500 