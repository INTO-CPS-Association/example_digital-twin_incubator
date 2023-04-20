import pika
import logging
import ssl as ssl_package

from communication.shared.protocol import *


class Rabbitmq:
    def __init__(self, ip,
                 port,
                 username,
                 password,
                 vhost,
                 exchange,
                 type,
                 ssl = None,
                 ):
        self._l = logging.getLogger("RabbitMQClass")
        self.vhost = vhost
        self.exchange_name = exchange
        self.exchange_type = type
        
        credentials = pika.PlainCredentials(username, password)
        if ssl is None:
            self.parameters = pika.ConnectionParameters(ip,
                                                        port,
                                                        vhost,
                                                        credentials)
        else:
            ssl_context = ssl_package.SSLContext(getattr(ssl_package, ssl["protocol"]))
            ssl_context.set_ciphers(ssl["ciphers"])

            self.parameters = pika.ConnectionParameters(ip,
                                                        port,
                                                        vhost,
                                                        credentials,
                                                        ssl_options=pika.SSLOptions(context=ssl_context))
        self.connection = None
        self.channel = None
        self.queue_name = []
        

    def __del__(self):
        self._l.debug("Deleting queues, close channel and connection")
        if self.channel is not None:
            if not self.channel.is_closed and not self.connection.is_closed:
                self.close()
        self._l.info("Connection closed.")

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        self._l.info("Connection closed.")

    def __enter__(self):
        self.connect_to_server()
        return self

    def connect_to_server(self):
        self.connection = pika.BlockingConnection(self.parameters)
        self._l.info("Connected.")
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange=self.exchange_name, exchange_type=self.exchange_type)

    def send_message(self, routing_key, message, properties=None):
        self.channel.basic_publish(exchange=self.exchange_name,
                                   routing_key=routing_key,
                                   body=encode_json(message),
                                   properties=properties
                                   )
        self._l.debug(f"Message sent to {routing_key}.")
        self._l.debug(message)

    def get_message(self, queue_name):
        (method, properties, body) = self.channel.basic_get(queue=queue_name, auto_ack=True)

        self._l.debug(f"Received message is {body} {method} {properties}")
        if body is not None:
            return decode_json(body)
        else:
            return None

    def declare_local_queue(self, routing_key):
        # Creates a local queue.
        # Rabbitmq server will clean it if the connection drops.
        result = self.channel.queue_declare(queue="", exclusive=True, auto_delete=True)
        created_queue_name = result.method.queue
        self.channel.queue_bind(
            exchange=self.exchange_name,
            queue=created_queue_name,
            routing_key=routing_key
        )
        self.queue_name.append(created_queue_name)
        self._l.info(f"Bound {routing_key}--> {created_queue_name}")
        return created_queue_name

    def queues_delete(self):
        self.queue_name = list(set(self.queue_name))
        for name in self.queue_name:
            self._l.debug(f"Deleting queue:{name}")
            self.channel.queue_unbind(queue=name, exchange=self.exchange_name)
            self.channel.queue_delete(queue=name)

    def close(self):
        self._l.debug("Deleting created queues by Rabbitmq class")
        self.queues_delete()
        self._l.debug("Closing channel in rabbitmq")
        self.channel.close()
        self._l.debug("Closing connection in rabbitmq")
        self.connection.close()

    def subscribe(self, routing_key, on_message_callback):
        created_queue_name = self.declare_local_queue(routing_key=routing_key)

        # Register an intermediate function to decode the msg.
        def decode_msg(ch, method, properties, body):
            body_json = decode_json(body)
            on_message_callback(ch, method, properties, body_json)

        self.channel.basic_consume(queue=created_queue_name,
                                   on_message_callback=decode_msg,
                                   auto_ack=True)
        return created_queue_name

    def start_consuming(self):
        self.channel.start_consuming()

