import uuid

import pika
import logging

from communication.server.rabbitmq import Rabbitmq
from communication.server.rpc_server import METHOD_ATTRIBUTE
from communication.shared.connection_parameters import *
from communication.shared.protocol import decode_json


class RPCClient(Rabbitmq):
    """
    Implements some basic operations to make it easier to implement remote procedure call as in
    https://www.rabbitmq.com/tutorials/tutorial-six-python.html
    """

    def __init__(self, ip=RASPBERRY_IP,
                 port=RASPBERRY_PORT,
                 username=PIKA_USERNAME,
                 password=PIKA_PASSWORD,
                 vhost=PIKA_VHOST,
                 exchange_name=PIKA_EXCHANGE,
                 exchange_type=PIKA_EXCHANGE_TYPE
                 ):
        super().__init__(ip=ip,
                         port=port,
                         username=username,
                         password=password,
                         vhost=vhost,
                         exchange_name=exchange_name,
                         exchange_type=exchange_type)
        self._l = logging.getLogger("RPCClient")
        self.reply_queue = None

    def connect_to_server(self):
        super(RPCClient, self).connect_to_server()
        result = self.channel.queue_declare(queue="", exclusive=True, auto_delete=True)
        self.reply_queue = result.method.queue

    def invoke_method(self, routing_key, method_to_invoke, arguments):
        corr_id = str(uuid.uuid4())
        assert METHOD_ATTRIBUTE not in arguments
        arguments[METHOD_ATTRIBUTE] = method_to_invoke
        self.send_message(routing_key=routing_key, message=arguments,
                          properties=pika.BasicProperties(
                              reply_to=self.reply_queue,
                              correlation_id=corr_id,
                          ))
        response = None
        # Stores the generator of reply messages
        messages_reply = self.channel.consume(self.reply_queue, auto_ack=True)
        while response is None:
            (method, properties, body) = next(messages_reply)
            self._l.debug(f"Message received: method={method}; properties={properties}. Body:\n{body}")
            if properties.correlation_id == corr_id:
                response = decode_json(body)
            else:
                self._l.warning(f"Unexpected message received:\n{body}")
        return response

