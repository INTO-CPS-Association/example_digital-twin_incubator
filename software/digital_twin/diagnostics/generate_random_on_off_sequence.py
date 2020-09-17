import sys
import pika
import json
import random
import time

sys.path.append("../../shared/")
from connection_parameters import *
from protocol import *


MIN_TIME = 10
MAX_TIME = 50

if __name__ == '__main__':
    credentials = pika.PlainCredentials(PIKA_USERNAME, PIKA_PASSWORD)
    parameters = pika.ConnectionParameters(RASPBERRY_IP,
                                           RASPBERRY_PORT,
                                           PIKA_VHOST,
                                           credentials)
    connection = pika.BlockingConnection(parameters)

    channel = connection.channel()
    channel.exchange_declare(exchange=PIKA_EXCHANGE, exchange_type=PIKA_EXCHANGE_TYPE)

    # Turn on Fan
    channel.basic_publish(exchange=PIKA_EXCHANGE, routing_key=ROUTING_KEY_FAN, body=str(True).encode(ENCODING))

    random.seed(1234)

    try:
        while True:
            on = random.choice([True, False])
            channel.basic_publish(exchange=PIKA_EXCHANGE, routing_key=ROUTING_KEY_HEATER, body=str(on).encode(ENCODING))
            print(f"Heater on: {on}")

            sleep_time = random.uniform(MIN_TIME, MAX_TIME)
            print(f"Sleeping for {sleep_time}s.")
            time.sleep(sleep_time)
    except: 
        connection.close()
        raise
