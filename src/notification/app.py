from flask import Flask
from scheduler import check_and_notify

app = Flask(__name__)

@app.route('/')
def home():
    return "Notification Service Running"

@app.route('/run-check')
def run_check():
    check_and_notify()
    return "Check ran", 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5005)