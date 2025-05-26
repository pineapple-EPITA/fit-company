from flask import Flask, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.models_dto import WODRequest, WODResponse
from services.wod_service import WODService

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'your-secret-key'  # In production, use environment variable

wod_service = WODService()

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200

@app.route('/wod', methods=['POST'])
@jwt_required()
def generate_wod():
    try:
        data = request.get_json()
        wod_request = WODRequest(
            user_id=get_jwt_identity(),
            fitness_level=data.get('fitness_level', 'beginner'),
            goals=data.get('goals', []),
            equipment_available=data.get('equipment_available', [])
        )
        
        wod_response = wod_service.generate_wod(wod_request)
        return jsonify(wod_response.dict()), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003) 