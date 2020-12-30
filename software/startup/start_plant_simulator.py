import logging

from digital_twin.models.plant_models.plant_simulator import PlantSimulator4Params
from startup.logging_config import config_logging

if __name__ == '__main__':
    config_logging(filename="simulator.log", level=logging.DEBUG)
    simulator = PlantSimulator4Params(ip="localhost")

    simulator.start_serving()
