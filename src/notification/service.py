notifications_store = {}

def send_notification(user_id, message):
    print(f"[NOTIFY] To user {user_id}: {message}")
    if user_id not in notifications_store:
        notifications_store[user_id] = []
    notifications_store[user_id].append(message)