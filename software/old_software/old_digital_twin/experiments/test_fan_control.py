import pika
import json

# sys.path.append("../../shared/")
from communication.shared.connection_parameters import *
from communication.shared.protocol import *


if __name__ == '__main__':
    credentials = pika.PlainCredentials(PIKA_USERNAME, PIKA_PASSWORD)
    parameters = pika.ConnectionParameters(RASPBERRY_IP,
                                           RASPBERRY_PORT,
                                           PIKA_VHOST,
                                           credentials)
    connection = pika.BlockingConnection(parameters)

    channel = connection.channel()
    channel.exchange_declare(exchange=PIKA_EXCHANGE, exchange_type=PIKA_EXCHANGE_TYPE)
    routing_key = ROUTING_KEY_FAN
    message = False
    channel.basic_publish(exchange=PIKA_EXCHANGE, routing_key=routing_key, body=str(message).encode(ENCODING))
    print(" [x] Sent %r:%r" % (routing_key, message))
    connection.close()