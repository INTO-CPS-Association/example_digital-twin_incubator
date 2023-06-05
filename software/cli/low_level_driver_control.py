import os
import argparse

from incubator.communication.shared.protocol import ROUTING_KEY_FAN, ROUTING_KEY_HEATER
from incubator.communication.server.rabbitmq import Rabbitmq
from incubator.config.config import config_logger, load_config


def _send_command(routing_key, message):
    config = load_config("startup.conf")
    with Rabbitmq(**config["rabbitmq"]) as rabbitmq:
        rabbitmq.send_message(routing_key=routing_key, message=message)


def _command_fan(args):
    print(f"Turning fan {args.command}...")
    message = {
        "fan": True if args.command == 'on' else False
    }
    _send_command(ROUTING_KEY_FAN, message)
    print(f"Command sent.")


def _command_heater(args):
    print(f"Turning heater {args.command}...")
    message = {
        "heater": True if args.command == 'on' else False
    }
    _send_command(ROUTING_KEY_HEATER, message)
    print(f"Command sent.")


def main():
    parser = argparse.ArgumentParser(description='Script to control the incubator.')

    script_name = os.path.basename(__file__)

    subparsers = parser.add_subparsers(
        help=f'Actuator to control. For help in each actuator run `{script_name} command -h`.',
        required=True
    )

    parser_fan = subparsers.add_parser('fan', help='Control the fan')
    parser_fan.add_argument('command', choices=['on', 'off'], help="Turns the fan on or off.")
    parser_fan.set_defaults(func=_command_fan)

    parser_heater = subparsers.add_parser('heater', help='Control the heater')
    parser_heater.add_argument('command', choices=['on', 'off'], help="Turns the heater on or off.")
    parser_heater.set_defaults(func=_command_heater)

    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    config_logger("logging.conf")
    main()
