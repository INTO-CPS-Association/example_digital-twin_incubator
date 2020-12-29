import pika
import logging

from communication.shared.connection_parameters import *
from communication.shared.protocol import decode_json, encode_json

METHOD_ATTRIBUTE = "method"


class RPCServer:
    """
    Implements some basic operations to make it easier to implement remote procedure call as in
    https://www.rabbitmq.com/tutorials/tutorial-six-python.html
    Subclasses should specialize this and implement the methods that can be invoked from rabbitmq messages.
    For instance, if a message contains a method attribute with "run", then the subclass should implement the "on_run" method.
    This server can be scaled horizontally, so beware of keeping state in python objects.
    Any state should be placed in a database.
    """

    def __init__(self, ip=RASPBERRY_IP,
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

        self.parameters = pika.ConnectionParameters(ip,
                                                    port,
                                                    vhost,
                                                    pika.PlainCredentials(username, password))
        self._l = logging.getLogger("RCPServer")

    def start_serving(self, routing_key, queue_name):
        connection = pika.BlockingConnection(self.parameters)
        channel = connection.channel()
        channel.exchange_declare(exchange=self.exchange_name, exchange_type=self.exchange_type)
        channel.queue_declare(queue=queue_name)
        channel.basic_qos(prefetch_count=1)
        channel.queue_bind(
            exchange=self.exchange_name,
            queue=queue_name,
            routing_key=routing_key
        )
        channel.basic_consume(queue=queue_name, on_message_callback=self.serve)
        self._l.debug(f"Listening for msgs in queue {queue_name} bound to topic {routing_key}")
        channel.start_consuming()

    def serve(self, ch, method, props, body):
        body_json = decode_json(body)
        self._l.debug(f"Message received: \nf{body_json}")

        # Check if reply_to is given
        if props.reply_to is None:
            self._l.warning(f"Message received does not have reply_to. Will be ignored. Message:\n{body_json}.")
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return

        routing_key_reply = props.reply_to
        self._l.debug(f"routing_key_reply = f{routing_key_reply}")

        request_id = props.correlation_id
        self._l.debug(f"request_id = f{request_id}")

        # Create short function to reply
        def reply(msg):
            ch.basic_publish(exchange='',
                            routing_key=routing_key_reply,
                            properties=pika.BasicProperties(correlation_id=request_id),
                            body=encode_json(msg))
            ch.basic_ack(delivery_tag=method.delivery_tag)

        # Check if method is provided
        if METHOD_ATTRIBUTE not in body_json:
            self._l.warning(f"Message received does not have attribute {METHOD_ATTRIBUTE}. Message:\n{body_json}")
            reply({"error": f"Attribute {METHOD_ATTRIBUTE} must be specified."})
            return

        server_method = body_json["method"]

        # Check if method exists in subclasses
        method_op = getattr(self, f"on_{server_method}", None)
        if method_op is None:
            self._l.warning(f"Method specified does not exist: {server_method}. Message:\n{body_json}")
            reply({"error": f"Method specified does not exist: {server_method}."})
            return

        # Call method
        reply_msg = method_op(body_json)
        self._l.debug(f"Sending reply msg:\n{reply_msg}")
        reply(reply_msg)

    def on_echo(self, request_msg):
        """
        Example method that is invoked by RPCServer when a message arrives with the method=echo
        """
        return request_msg