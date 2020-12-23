import logging
import time

from communication.server.rabbitmq import Rabbitmq

if __name__ == '__main__':
    logging.basicConfig(level=logging.ERROR)

    receiver = Rabbitmq(ip_raspberry="localhost")
    receiver.connect_to_server()
    receiver.declare_queue(queue_name='test_queue', routing_key="test")


    sender = Rabbitmq(ip_raspberry="localhost")
    sender.connect_to_server()
    sender.send_message(routing_key="test", message="321")

    time.sleep(0.01)  # in case too fast that the message has not been delivered.

    msg = receiver.get_message(queue_name="test_queue", binding_key="test")
    print("received message is", msg)

