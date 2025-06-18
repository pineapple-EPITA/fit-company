import pika
import json
from service import send_notification

def callback(ch, method, properties, body):
    try:
        message = json.loads(body)
        msg_type = message.get("type")
        user_email = message.get("user_email")
        print(f"[x] Received {msg_type} for {user_email}: {message}")

        if msg_type == "subscription_activated":
            end_date = message.get("end_date")
            send_notification(user_email, f"Your subscription is now active until {end_date}.")

        elif msg_type == "subscription_expiring":
            days = message.get("days_until_expiry")
            send_notification(user_email, f"Your subscription will expire in {days} days. Renew soon!")

        elif msg_type == "subscription_cancelled":
            send_notification(user_email, "Your subscription has been cancelled.")
        else:
            print("Unknown message type:", msg_type)

        # Explicit ACK here
        print(f"[x] ACKing message for {user_email}")
        ch.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:
        print("Failed to process message:", e)
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

def start_consumer():
    print("Connecting to RabbitMQ...")

    credentials = pika.PlainCredentials("rabbit", "docker")
    parameters = pika.ConnectionParameters(
        host="rabbitmq",
        port=5672,
        credentials=credentials,
        heartbeat=600,
        blocked_connection_timeout=300
    )
    
    try:
        connection = pika.BlockingConnection(parameters)
        print("Connected to RabbitMQ")
    except Exception as e:
        print("Failed to connect to RabbitMQ:", e)
        return

    channel = connection.channel()
    channel.queue_declare(queue="billing_queue", durable=True)

    print("[*] Waiting for messages in billing. To exit press CTRL+C")

    channel.basic_qos(prefetch_count=1)

    channel.basic_consume(
        queue="billing_queue",
        on_message_callback=callback,
        auto_ack=False
    )

    channel.start_consuming()
