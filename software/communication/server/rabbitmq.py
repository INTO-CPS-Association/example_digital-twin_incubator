import pika
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
        self.connection = pika.BlockingConnection(self.parameters)
        self.logger.info("Connected.")
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange=self.exchange_name, exchange_type=self.exchange_type)

    def send_message(self, routing_key, message=''):
        self.channel.basic_publish(exchange=self.exchange_name,
                                   routing_key=routing_key,
                                   body=str(message).encode(ENCODING)
                                   )
        self.logger.debug(f"Message sent to {routing_key}.")
        self.logger.debug(message)
        self.logger.info("Message Sent.")

    def get_message(self, queue_name):
        self.logger.debug("Creating a new queue.")
        (method, properties, body) = self.channel.basic_get(queue=queue_name, auto_ack=True)

        self.logger.debug(f"Received message is {body} {method} {properties}")
        if body is not None:
            return eval(body)
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
        print("Deleting created queues by Rabbitmq class")
        self.queues_delete()
        print("Closing channel in rabbitmq")
        self.channel.close()
        print("Closing connection in rabbitmq")
        self.connection.close()


if __name__ == '__main__':
    logging.basicConfig(level=logging.ERROR)

    receiver = Rabbitmq(ip_raspberry="localhost")
    receiver.connect_to_server()
    receiver.declare_queue(queue_name='test_queue', routing_key="test")

    sender = Rabbitmq(ip_raspberry="localhost")
    sender.connect_to_server()
    sender.send_message(routing_key="test", message="321")

    time.sleep(0.01)  # in case too fast that the message has not been delivered.

    msg = receiver.get_message(queue_name="test_queue")
    print("received message is", msg)

    # test_send.channel.queue_purge('test_queue')

    # test_send.close()
    # test_receive.close()
