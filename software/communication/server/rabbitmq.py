import pika
import json
import logging
import time

try:
    from communication.shared.connection_parameters import *
    from communication.shared.protocol import *
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
        self.queue_name = []
        # self.routing_key = None
        self.method = None
        self.properties = None
        self.body = None
        self.logger = logging.getLogger("RabbitMQ Class")

    def __del__(self):
        self.logger.debug("Deleting queues, close channel and connection")
        if not self.channel.is_closed and not self.connection.is_closed:
            self.close()
        self.logger.info("Connection closed.")

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        self.logger.info("Connection closed.")

    def __enter__(self):
        self.connect_to_server()

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
        # self.routing_key = routing_key
        # self.declare_queue(queue_name=queue_name, routing_key=routing_key)
        self.channel.basic_publish(exchange=self.exchange_name,
                                   routing_key=routing_key,
                                   body=str(message).encode(ENCODING)#  json.dumps(message)
                                   # bytes(message, ENCODING)
                                   )
        self.logger.debug(f"Message sent to {routing_key}.")
        self.logger.debug(message)
        self.logger.info("Message Sent.")

    def get_message(self, queue_name, binding_key):
        self.logger.debug("Creating a new queue.")
        # print("creating a new queue")
        self.declare_queue(queue_name=queue_name, routing_key=binding_key)
        (self.method, self.properties, self.body) = self.channel.basic_get(queue=queue_name,
                                                                           auto_ack=True)

        self.logger.debug(f"Received message is {self.body} {self.method} {self.properties}")
        # print("body is", self.body, self.method, self.properties)
        if self.body is not None:
            return eval(self.body)
        else:
            return None

    def declare_queue(self, queue_name, routing_key):
        self.channel.queue_declare(queue_name)
        self.channel.queue_bind(
            exchange=self.exchange_name,
            queue=queue_name,
            routing_key=routing_key
        )
        self.queue_name.append(queue_name)
        self.logger.info(f"Bound {routing_key}--> {queue_name}")

    def queues_delete(self):
        self.queue_name = list(set(self.queue_name))
        for name in self.queue_name:
            self.logger.debug(f"Deleting queue:{name}")
            self.channel.queue_unbind(queue=name, exchange=self.exchange_name)
            self.channel.queue_delete(queue=name)

    def close(self):
        self.queues_delete()
        self.channel.close()
        self.connection.close()


if __name__ == '__main__':
    logging.basicConfig(level=logging.ERROR)

    receiver = Rabbitmq()
    receiver.connect_to_server()
    receiver.declare_queue(queue_name='test_queue', routing_key="test")

    sender = Rabbitmq()
    sender.connect_to_server()
    sender.send_message(routing_key="test", message="321")

    time.sleep(0.01)  # in case too fast that the message has not been delivered.
    receiver.get_message(queue_name="test_queue", binding_key="test")
    print("received message is", receiver.body)

    receiver.get_message(queue_name="test_queue", binding_key="test")
    print("received message is", receiver.body)

    # test_send.channel.queue_purge('test_queue')

    # test_send.close()
    # test_receive.close()
