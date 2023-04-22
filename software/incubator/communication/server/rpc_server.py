import inspect

import pika
import logging

from incubator.communication.shared.protocol import decode_json, encode_json

METHOD_ATTRIBUTE = "method"
ARGS_ATTRIBUTE = "args"


class RPCServer:
    """
    Implements some basic operations to make it easier to implement remote procedure call as in
    https://www.rabbitmq.com/tutorials/tutorial-six-python.html
    Subclasses should specialize this and implement the methods that can be invoked from rabbitmq messages.
    For instance, if a message contains a method attribute with "run", then the subclass should implement the "on_run" method.
    This server can be scaled horizontally, so beware of keeping state in python objects.
    Any state should be placed in a database.
    """
    
    def __init__(self, ip,
                 port,
                 username,
                 password,
                 vhost,
                 exchange,
                 type
                 ):
        self.vhost = vhost
        self.exchange_name = exchange
        self.exchange_type = type
        self.ip = ip
        self.parameters = pika.ConnectionParameters(ip,
                                                    port,
                                                    vhost,
                                                    pika.PlainCredentials(username, password))
        self._l = logging.getLogger("RCPServer")
        self.channel = None

    def setup(self, routing_key, queue_name):
        connection = pika.BlockingConnection(self.parameters)
        self.channel = connection.channel()
        self.channel.exchange_declare(exchange=self.exchange_name, exchange_type=self.exchange_type)
        self.channel.queue_declare(queue=queue_name)
        self.channel.basic_qos(prefetch_count=1)
        self.channel.queue_bind(
            exchange=self.exchange_name,
            queue=queue_name,
            routing_key=routing_key
        )
        self.channel.basic_consume(queue=queue_name, on_message_callback=self.serve)
        self._l.debug(f"Ready to listen for msgs in queue {queue_name} bound to topic {routing_key}")

    def start_serving(self):
        self.channel.start_consuming()

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
            self._l.debug(f"Sending reply msg:\n{msg}")
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

        server_method = body_json[METHOD_ATTRIBUTE]

        # Check if method exists in subclasses
        method_op = getattr(self, server_method, None)
        if method_op is None:
            self._l.warning(f"Method specified does not exist: {server_method}. Message:\n{body_json}")
            reply({"error": f"Method specified does not exist: {server_method}."})
            return

        # Check if args are provided
        if ARGS_ATTRIBUTE not in body_json:
            self._l.warning(
                f"Message received does not have arguments in attribute {ARGS_ATTRIBUTE}. Message:\n{body_json}")
            reply({"error": f"Message received does not have arguments in attribute {ARGS_ATTRIBUTE}."})
            return
        args = body_json[ARGS_ATTRIBUTE]

        # Get method signature and compare it with args provided
        # This ensures that methods are called with the arguments in their signature.
        signature = inspect.signature(method_op)
        if "reply_fun" not in signature.parameters:
            error_msg = f"Method {method_op} must declare a parameter 'reply_fun' that must be invoked to reply to an invokation."
            self._l.warning(error_msg)
            reply({"error": error_msg})
            return
        for arg_name in signature.parameters:
            if arg_name != "reply_fun" and arg_name not in args:
                self._l.warning(
                    f"Message received does not specify argument {arg_name} in attribute {ARGS_ATTRIBUTE}. Message:\n{body_json}")
                reply({"error": f"Message received does not specify argument {arg_name} in attribute {ARGS_ATTRIBUTE}."})
                return

        # Call method with named arguments provided.
        method_op(**args, reply_fun=reply)

    def echo(self, msg, reply_fun):
        """
        Example method that is invoked by RPCServer when a message arrives with the method=echo
        """

        """
        This send the reply message back.
        Instead of returning, this solution allows child classes to, e.g., reply and start listening for other messages.
        """
        reply_fun(msg)