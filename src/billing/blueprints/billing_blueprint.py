from flask import Blueprint, request, jsonify
from pydantic import ValidationError
from ..services.billing_service import BillingService
from ..models_dto import SubscriptionCreate, PaymentCreate

billing_bp = Blueprint('billing', __name__)

@billing_bp.route('/subscriptions', methods=['POST'])
def create_subscription():
    try:
        data = request.get_json()
        subscription_data = SubscriptionCreate.model_validate(data)
        subscription = BillingService.create_subscription(subscription_data)
        return jsonify(subscription.model_dump()), 201
    except ValidationError as e:
        return jsonify({"error": "Invalid subscription data", "details": e.errors()}), 400
    except Exception as e:
        return jsonify({"error": "Error creating subscription", "details": str(e)}), 500

@billing_bp.route('/subscriptions/<int:subscription_id>/payments', methods=['POST'])
def process_payment(subscription_id):
    try:
        data = request.get_json()
        payment_data = PaymentCreate.model_validate(data)
        payment = BillingService.process_payment(subscription_id, payment_data)
        return jsonify(payment.model_dump()), 201
    except ValidationError as e:
        return jsonify({"error": "Invalid payment data", "details": e.errors()}), 400
    except Exception as e:
        return jsonify({"error": "Error processing payment", "details": str(e)}), 500

@billing_bp.route('/subscriptions/<int:subscription_id>', methods=['GET'])
def get_subscription(subscription_id):
    try:
        subscription = BillingService.get_subscription(subscription_id)
        if subscription:
            return jsonify(subscription.model_dump()), 200
        return jsonify({"error": "Subscription not found"}), 404
    except Exception as e:
        return jsonify({"error": "Error retrieving subscription", "details": str(e)}), 500

@billing_bp.route('/users/<int:user_id>/subscriptions', methods=['GET'])
def get_user_subscriptions(user_id):
    try:
        subscriptions = BillingService.get_user_subscriptions(user_id)
        return jsonify([sub.model_dump() for sub in subscriptions]), 200
    except Exception as e:
        return jsonify({"error": "Error retrieving user subscriptions", "details": str(e)}), 500

@billing_bp.route('/subscriptions/<int:subscription_id>/cancel', methods=['POST'])
def cancel_subscription(subscription_id):
    try:
        subscription = BillingService.cancel_subscription(subscription_id)
        if subscription:
            return jsonify(subscription.model_dump()), 200
        return jsonify({"error": "Subscription not found"}), 404
    except Exception as e:
        return jsonify({"error": "Error cancelling subscription", "details": str(e)}), 500

@billing_bp.route('/subscriptions/expiring', methods=['GET'])
def get_expiring_subscriptions():
    try:
        days = request.args.get('days', default=7, type=int)
        subscriptions = BillingService.check_expiring_subscriptions(days)
        return jsonify([sub.model_dump() for sub in subscriptions]), 200
    except Exception as e:
        return jsonify({"error": "Error retrieving expiring subscriptions", "details": str(e)}), 500 