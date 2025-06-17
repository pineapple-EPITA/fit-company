from flask import Flask
from threading import Thread
from queue_consumer import start_consumer
from scheduler import check_and_notify
from service import notifications_store

app = Flask(__name__)

@app.route('/')
def home():
    return "Notification Service Running"

@app.route('/run-check')
def run_check():
    check_and_notify()
    return "Check ran", 200

@app.route('/notifications/<user_id>')
def get_notifications(user_id):
    notifications = notifications_store.get(user_id, [])
    return {"notifications": notifications}, 200

def start_consumer_thread():
    consumer_thread = Thread(target=start_consumer)
    consumer_thread.daemon = True
    consumer_thread.start()

start_consumer_thread()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5005)
