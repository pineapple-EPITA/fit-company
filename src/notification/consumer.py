import pika

def callback(ch, method, properties, body):
    print(f" [x] Received: {body.decode()}")  # or send email/push

def start_consumer():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
    channel = connection.channel()

    # Declare the same queue that billing publishes to
    channel.queue_declare(queue='workoutCreatedQueue', durable=True)

    channel.basic_consume(
        queue='workoutCreatedQueue',
        on_message_callback=callback,
        auto_ack=True
    )

    print(" [*] Waiting for messages. To exit press CTRL+C")
    channel.start_consuming()