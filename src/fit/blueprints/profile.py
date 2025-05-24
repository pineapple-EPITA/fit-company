from flask import Blueprint, request, jsonify, g
from pydantic import ValidationError
from ..models_dto import UserProfileSchema
from ..services.user_service import update_user_profile, get_user_profile
from ..services.auth_service import jwt_required

profile_bp = Blueprint('profile', __name__)

@profile_bp.route("/profile/onboarding", methods=["POST"])
@jwt_required
def onboard_user():
    try:
        user_email = g.user_email
        profile_data = request.get_json()
        profile = UserProfileSchema.model_validate(profile_data)
        
        updated_profile = update_user_profile(user_email, profile)
        if not updated_profile:
            return jsonify({"error": "User not found"}), 404
            
        return jsonify(updated_profile.model_dump()), 200
        
    except ValidationError as e:
        return jsonify({"error": "Invalid profile data", "details": e.errors()}), 400
    except Exception as e:
        return jsonify({"error": "Error updating profile", "details": str(e)}), 500

@profile_bp.route("/profile", methods=["GET"])
@jwt_required
def get_profile():
    try:
        user_email = g.user_email
        profile = get_user_profile(user_email)
        if not profile:
            return jsonify({"error": "User not found"}), 404
            
        return jsonify(profile.model_dump()), 200
        
    except Exception as e:
        return jsonify({"error": "Error retrieving profile", "details": str(e)}), 500 