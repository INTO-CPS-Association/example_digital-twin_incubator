import pika
import json

# sys.path.append("../../shared/")
from communication.shared.connection_parameters import *
from communication.shared.protocol import *

RASPBERRY_IP = "10.17.98.239"
RASPBERRY_PORT = 5672
PIKA_USERNAME = "incubator"
PIKA_PASSWORD = "incubator"
PIKA_EXCHANGE = "Incubator_AMQP"
PIKA_EXCHANGE_TYPE = "topic"
PIKA_VHOST = "/"

ROUTING_KEY_STATE = "incubator.driver.state"
ROUTING_KEY_HEATER = "incubator.hardware.gpio.heater.on"
ROUTING_KEY_FAN = "incubator.hardware.gpio.fan.on"
ENCODING = "ascii"
HEAT_CTRL_QUEUE = "heater_control"
FAN_CTRL_QUEUE = "fan_control"


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