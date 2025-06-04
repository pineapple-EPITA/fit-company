from flask import Blueprint, jsonify, request
from ..database import db_session
from ..models_db import UserModel
from ..queue.rabbitmq import rabbitmq_client
from datetime import date, datetime, UTC

wod_bp = Blueprint('wod', __name__)

@wod_bp.route("/create-all", methods=["POST"])
def create_wods_for_all_users():
    """Create WOD requests for all users"""
    try:
        db = db_session()
        users = db.query(UserModel).all()
        db.close()

        if not users:
            return jsonify({"error": "No users found"}), 404

        created_requests = []
        for user in users:
            request_id = str(datetime.now(UTC).timestamp())
            message = {
                "user_email": user.email,
                "date": date.today().isoformat()
            }
            rabbitmq_client.publish_message(message)
            created_requests.append({
                "request_id": request_id,
                "user_email": user.email
            })

        return jsonify({
            "message": f"Created WOD requests for {len(created_requests)} users",
            "requests": created_requests
        }), 202

    except Exception as e:
        return jsonify({"error": f"Failed to create WOD requests: {str(e)}"}), 500 