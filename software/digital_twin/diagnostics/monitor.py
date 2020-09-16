import sys
import pika
import json

sys.path.append("../../shared/")
from connection_parameters import *
from protocol import *


def read_state(ch, method, properties, body):
    print(body)

if __name__ == '__main__':
    credentials = pika.PlainCredentials(PIKA_USERNAME, PIKA_PASSWORD)
    parameters = pika.ConnectionParameters(RASPBERRY_IP,
                                           RASPBERRY_PORT,
                                           PIKA_VHOST,
                                           credentials)
    connection = pika.BlockingConnection(parameters)

    channel = connection.channel()
    channel.exchange_declare(exchange=PIKA_EXCHANGE, exchange_type=PIKA_EXCHANGE_TYPE)
    
    queue_name = "monitor"
    channel.queue_declare(queue_name, exclusive=True)
    channel.queue_bind(
            exchange=PIKA_EXCHANGE,
            queue=queue_name,
            routing_key=ROUTING_KEY_STATE
        )
    
    channel.basic_consume(queue=queue_name, on_message_callback=read_state, auto_ack=True)

    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        connection.close()