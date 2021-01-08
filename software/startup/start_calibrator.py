from config.config import config_logger, load_config
from digital_twin.calibration.plant_calibrator import PlantCalibrator4Params


def start_calibrator(ok_queue=None):
    config_logger("logging.conf")
    config = load_config("startup.conf")
    service = PlantCalibrator4Params(rabbitmq_config=config["rabbitmq"], influxdb_config=config["influxdb"])

    service.setup()

    if ok_queue is not None:
        ok_queue.put("OK")

    service.start_serving()


if __name__ == '__main__':
    start_calibrator()
