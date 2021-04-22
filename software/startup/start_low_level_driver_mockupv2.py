from pathlib import Path

from incubator.experiments.config.config import load_config, config_logger
import logging

from physical.software.shared.low_level_driver_server import IncubatorDriver

from mock_plant.mock_connection import MOCK_TEMP_T1, MOCK_TEMP_T2, MOCK_TEMP_T3
from mock_plant.mock_sensors_actuators import HeaterMock, LedMock, TemperatureSensorMock


def start_low_level_driver_mockupv2(ok_queue, configuration, logging_configuration):
    config = load_config(configuration)

    logging.basicConfig(level=logging.INFO)
    if Path(logging_configuration).exists():
        config_logger(logging_configuration)

    incubator = IncubatorDriver(rabbit_config=config["rabbitmq"],
                                heater=HeaterMock(config["rabbitmq"]),
                                fan=LedMock(),
                                t1=TemperatureSensorMock(MOCK_TEMP_T1, config["rabbitmq"]),
                                t2=TemperatureSensorMock(MOCK_TEMP_T2, config["rabbitmq"]),
                                t3=TemperatureSensorMock(MOCK_TEMP_T3, config["rabbitmq"]),
                                simulate_actuation=False)
    incubator.setup()
    if ok_queue is not None:
        ok_queue.put("OK")
    incubator.control_loop()


def main():
    import argparse

    options = argparse.ArgumentParser(prog="low_level_driver_server")
    options.add_argument("-log", "--log-conf", dest="log_conf", type=str, required=False, help='Path to a log conf file',default="logging.conf")
    options.add_argument("-c", "--conf", dest="conf", type=str, required=True,
                         help='Path to the config file',default='startup.conf')

    args = options.parse_args()

    logging.basicConfig(level=logging.INFO)
    if Path(args.log_conf).exists():
        config_logger(args.log_conf)
    config = load_config(args.conf)

    start_low_level_driver_mockupv2(config)

if __name__ == '__main__':
    main()