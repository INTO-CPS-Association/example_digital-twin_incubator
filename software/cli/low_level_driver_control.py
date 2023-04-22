from incubator.communication.shared.protocol import ROUTING_KEY_FAN, ROUTING_KEY_HEATER
from incubator.communication.server.rabbitmq import Rabbitmq
from incubator.config.config import config_logger, load_config

if __name__ == '__main__':
    config_logger("logging.conf")
    config = load_config("startup.conf")

    with Rabbitmq(**config["rabbitmq"]) as rabbitmq:
        # rabbitmq.send_message(routing_key=ROUTING_KEY_FAN, message={"fan": False})
        rabbitmq.send_message(routing_key=ROUTING_KEY_HEATER, message={"heater": False})