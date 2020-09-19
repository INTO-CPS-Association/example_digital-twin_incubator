import sys
import pika
import json

sys.path.append("../../shared/")
from connection_parameters import *
from protocol import *


if __name__ == '__main__':
    credentials = pika.PlainCredentials(PIKA_USERNAME, PIKA_PASSWORD)
    parameters = pika.ConnectionParameters(RASPBERRY_IP,
                                           RASPBERRY_PORT,
                                           PIKA_VHOST,
                                           credentials)
    connection = pika.BlockingConnection(parameters)

    channel = connection.channel()
    channel.exchange_declare(exchange=PIKA_EXCHANGE, exchange_type=PIKA_EXCHANGE_TYPE)
    routing_key = ROUTING_KEY_HEATER
    try:
        while True:
            idx = int(input("0-Off, 1-On: "))
            on = [False, True][idx]
            channel.basic_publish(exchange=PIKA_EXCHANGE, routing_key=ROUTING_KEY_HEATER, body=str(on).encode(ENCODING))
            print(f"Heater on: {on}")
    except: 
        channel.basic_publish(exchange=PIKA_EXCHANGE, routing_key=ROUTING_KEY_HEATER, body=str(False).encode(ENCODING))
        connection.close()
        raise