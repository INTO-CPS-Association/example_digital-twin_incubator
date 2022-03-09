from incubator.communication.server.rabbitmq import Rabbitmq
from incubator.config.config import config_logger, load_config
from mock_plant.mock_connection import MOCK_G_BOX


def send_G_box_config(config, G_box):
    with Rabbitmq(**config) as rabbitmq:
        rabbitmq.send_message(MOCK_G_BOX, {
            "G_box": G_box
        })


if __name__ == '__main__':
    config_logger("logging.conf")
    config = load_config("startup.conf")

    # send_G_box_config(config["rabbitmq"], config["digital_twin"]["models"]["plant"]["param4"]["G_box"])
    send_G_box_config(config["rabbitmq"], 100*config["digital_twin"]["models"]["plant"]["param4"]["G_box"])
