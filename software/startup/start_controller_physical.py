import logging

from physical_twin.controller_physical import ControllerPhysical
from startup.logging_config import config_logging

if __name__ == '__main__':
    config_logging("ctrl.log", level=logging.WARN)
    controller = ControllerPhysical(rabbitmq_ip="localhost", desired_temperature=35.0)
    controller.start_control()
