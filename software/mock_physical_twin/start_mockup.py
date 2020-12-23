import logging

if __name__ == '__main__':
    logging.basicConfig(level=logging.ERROR)

    receiver = Rabbitmq(ip_raspberry="localhost")
    receiver.connect_to_server()
    receiver.declare_queue(queue_name='test_queue', routing_key="test")
