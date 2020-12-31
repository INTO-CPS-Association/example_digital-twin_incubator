import logging

from digital_twin.calibration.plant_calibrator import PlantCalibrator4Params
from startup.logging_config import config_logging

if __name__ == '__main__':
    config_logging(filename="calibrator.log", level=logging.DEBUG)
    calibrator = PlantCalibrator4Params(ip="localhost")

    calibrator.start_serving()
