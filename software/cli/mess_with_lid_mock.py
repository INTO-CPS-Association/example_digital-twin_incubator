from incubator.communication.server.rabbitmq import Rabbitmq
from incubator.config.config import config_logger, load_config
from mock_plant.mock_connection import MOCK_G_BOX
import argparse


def send_G_box_config(config, G_box):
    with Rabbitmq(**config) as rabbitmq:
        rabbitmq.send_message(MOCK_G_BOX, {"G_box": G_box})


if __name__ == "__main__":

    def positive_number(string):
        value = float(string)
        if value <= 0:
            raise argparse.ArgumentTypeError("%r is not a positive number" % string)
        return value

    parser = argparse.ArgumentParser(
        description="Enter a number to multiply the Incubator config G_box with."
    )
    parser.add_argument(
        "number",
        type=positive_number,
        help="Number to multiply the Incubator config G_box with.",
    )
    args = parser.parse_args()

    config_logger("logging.conf")
    config = load_config("startup.conf")

    new_G_box = (
        args.number * config["digital_twin"]["models"]["plant"]["param4"]["G_box"]
    )
    print(f"Setting G_box to: {new_G_box}")
    send_G_box_config(config["rabbitmq"], new_G_box)
