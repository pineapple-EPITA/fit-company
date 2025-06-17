import requests
from service import send_notification

def check_and_notify():
    try:
        response = requests.get("http://billing:5000/billing/subscriptions/expiring?days=3")
        expiring_subs = response.json()

        for sub in expiring_subs:
            user_id = sub["user_id"]
            end_date = sub["end_date"]
            send_notification(user_id, f"Your subscription will expire on {end_date}. Please renew to keep access.")
    except Exception as e:
        print("Error checking subscriptions:", str(e))
