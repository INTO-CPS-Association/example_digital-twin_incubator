from config.config import config_logger, load_config
from digital_twin.models.plant_models.plant_simulator import PlantSimulator4Params


def start_plant_simulator(ok_queue=None):
    config_logger("../logging.conf")
    config = load_config("../startup.conf")
    simulator = PlantSimulator4Params(rabbitmq_config=config["rabbitmq"], influxdb_config=config["influxdb"])

    simulator.setup()

    if ok_queue is not None:
        ok_queue.put("OK")

    simulator.start_serving()


if __name__ == '__main__':
    start_plant_simulator()