import sys
import pika
import json
import logging
sys.path.append("../shared")
try:
    from connection_parameters import *
    from protocol import *
except:
    raise

class Rabbitmq:
    def __init__(self, ip_raspberry=RASPBERRY_IP,
                 port=RASPBERRY_PORT,
                 username=PIKA_USERNAME,
                 password=PIKA_PASSWORD,
                 vhost=PIKA_VHOST,
                 exchange_name=PIKA_EXCHANGE,
                 exchange_type=PIKA_EXCHANGE_TYPE
                 ):
        self.vhost = vhost
        self.exchange_name = exchange_name
        self.exchange_type = exchange_type

        self.credentials = pika.PlainCredentials(username, password)
        self.parameters = pika.ConnectionParameters(ip_raspberry,
                                                    port,
                                                    vhost,
                                                    self.credentials)
        self.connection = None
        self.channel = None
        self.queue_name = None
        self.routing_key = None
        self.method = None
        self.properties = None
        self.body = None
        self.logger = logging.getLogger("RabbitMQ Class")

    def __del__(self):
        self.connection.close()
        self.logger.info("Connection closed.")

    def connect_to_server(self):
        # self.queue_name = queue_name
        # self.routing_key = routing_key
        self.connection = pika.BlockingConnection(self.parameters)
        self.logger.info("Connected.")
        # print("connected")
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange=self.exchange_name, exchange_type=self.exchange_type)

        # self.declare_queue(queue_name=self.queue_name,
        #                    routing_key=self.routing_key)

    def send_message(self, routing_key, message=''):
        self.channel.basic_publish(
            exchange=self.exchange_name, routing_key=routing_key, body= bytes(message,ENCODING))
        self.logger.debug(f"Message sent to {ROUTING_KEY_STATE}.")
        self.logger.debug(message)
        self.logger.info("Message Sent.")

    def get_message(self, queue_name, routing_key):
        if self.queue_name != queue_name and self.routing_key != routing_key:
            self.queue_name = queue_name
            self.routing_key = routing_key
            # print("Creating a new queue.")
            self.logger.debug("Creating a new queue.")
            # print("creating a new queue")
            self.declare_queue(queue_name=self.queue_name,routing_key=self.routing_key)

        (self.method, self.properties, self.body) = self.channel.basic_get(queue=self.queue_name,
                                                                           auto_ack=True)
        self.logger.debug(f"Received message is {self.body} {self.method} {self.properties}")
        print("body is",self.body,self.method,self.properties)
        return self._convert_str_to_bool(self.body)

    def declare_queue(self, queue_name, routing_key):
        self.channel.queue_declare(queue_name, exclusive=True)
        self.channel.queue_bind(
            exchange=self.exchange_name,
            queue=queue_name,
            routing_key=routing_key
        )
        self.logger.info(f"Bound {routing_key}--> {queue_name}")

    def _convert_str_to_bool(self, body):
        self.body = body
        if self.body is None:
            return None
        else:
            return self.body.decode(ENCODING) == "True"


if __name__ == '__main__':
    logging.basicConfig(level=logging.WARNING)
    # test_receive.declare_queue(queue_name="sdfd", routing_key="asd")
    # test_receive.get_message(queue_name="sdfd", routing_key="asd")

    test_send = Rabbitmq()
    test_send.connect_to_server()
    test_send.send_message(routing_key="test",message="321")
    test_send.send_message(routing_key="test", message="321")
    test_send.send_message(routing_key="test", message="321")
    # import time
    # time.sleep(4)
    # print("received message is", test_receive.body)
    test_receive = Rabbitmq()
    test_receive.connect_to_server()

    test_receive.get_message(queue_name="test_queue",routing_key="test")
    print("received message 1st is",test_receive.body)
    # print(test_receive.body)

    # test_send.send_message(routing_key="asd", message="321")
    test_receive.get_message(queue_name="test_queue",routing_key="test")
    print("received message 2nd is",test_receive.body)
