notifications_store = {}
sent_notifications = set()

def send_notification(user_email, message):
    key = (user_email, message)
    if key in sent_notifications:
        return

    print(f"[NOTIFY] To user {user_email}: {message}")
    sent_notifications.add(key)

    if user_email not in notifications_store:
        notifications_store[user_email] = []
    notifications_store[user_email].append(message)
