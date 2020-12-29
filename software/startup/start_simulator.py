import logging

from communication.shared.protocol import ROUTING_KEY_PTSIMULATOR4
from digital_twin.models.physical_twin_models.physical_twin_simulator4 import PhysicalTwinSimulator4Params
from startup.logging_config import config_logging

if __name__ == '__main__':
    config_logging("simulator.log", level=logging.WARN)
    simulator = PhysicalTwinSimulator4Params(ip="localhost")

    simulator.start_serving()
