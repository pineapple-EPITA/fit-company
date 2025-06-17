import pika
import json

connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
channel = connection.channel()
channel.queue_declare(queue='notificationQueue')

message = {'type': 'test', 'message': 'hello from billing!'}
channel.basic_publish(exchange='',
                      routing_key='notificationQueue',
                      body=json.dumps(message))

print("Test message sent.")
connection.close()