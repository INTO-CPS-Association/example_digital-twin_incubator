import logging
import time

from communication.server.rabbitmq import Rabbitmq

if __name__ == '__main__':
    logging.basicConfig(level=logging.WARNING)
    
    rabbbitmq_config = {
        "ip": "localhost",
        "port": 5672,
        "username": "incubator",
        "password": "incubator",
        "exchange": "Incubator_AMQP",
        "type": "topic",
        "vhost": "/"
    }
    
    # Example configuration for AMAZON AWS MQ Service. From https://docs.aws.amazon.com/amazon-mq/latest/developer-guide/amazon-mq-rabbitmq-pika.html
    rabbbitmq_config = {
        "ip": "CONTACT_CLAUDIO",
        "port": 5671,
        "username": "incubator",
        "password": "CONTACT_CLAUDIO",
        "exchange": "example_exchange",
        "type": "topic",
        "vhost": "incubator",
        "ssl": {
            "protocol": "PROTOCOL_TLS",
            "ciphers" : "ECDHE+AESGCM:!ECDSA"
        }
    }

    with Rabbitmq(**rabbbitmq_config) as connection:

        qname = connection.declare_local_queue(routing_key="test")

        print("Sending message...")
        connection.send_message(routing_key="test", message={"text": "321"})
        print("Message sent.")

        msg = None
        print("Retrieving message.", end="")
        while msg is None:
            msg = connection.get_message(queue_name=qname)
            if msg is not None:
                print(" Received message is", msg)
            else:
                print(".", end="")
                time.sleep(0.1)  # in case too fast that the message has not been delivered.


