import sys
import pika

sys.path.append("../shared")
from connection_parameters import *
from protocol import *

class Rabbitmq:
    HEAT_CTRL_QUEUE = "heater_control"
    FAN_CTRL_QUEUE = "fan_control"

    def __init__(self,ip_raspberry=RASPBERRY_IP,
                 port=RASPBERRY_PORT,
                 username=PIKA_USERNAME,
                 password=PIKA_PASSWORD,
                 vhost=PIKA_VHOST,
                 exchange_name=PIKA_EXCHANGE,
                 exchange_type=PIKA_EXCHANGE_TYPE):
        self.vhost = vhost
        self.exchange_name = exchange_name
        self.exchange_type = exchange_type

        credentials = pika.PlainCredentials(username, password)
        self.parameters = pika.ConnectionParameters(ip_raspberry,
                                                    port,
                                                    vhost,
                                                    credentials)
        self.connection = None
        self.channel = None

    def connection(self):
        self.connection = pika.BlockingConnection(self.parameters)
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange=self.exchange_name, exchange_type=self.exchange_type)

        self.declare_queue(queue_name=self.FAN_CTRL_QUEUE,
                           routing_key=ROUTING_KEY_FAN)
        self.declare_queue(queue_name=self.HEAT_CTRL_QUEUE,
                           routing_key=ROUTING_KEY_HEATER)

    def send_message(self):
        return 0

    def get_message(self):
        return 0

    def declare_queue(self, queue_name, routing_key):
        self.channel.queue_declare(queue_name, exclusive=True)
        self.channel.queue_bind(
            exchange=self.exchange_name,
            queue=queue_name,
            routing_key=routing_key
        )


