from digital_twin.simulator.physical_twin_simulator4 import PhysicalTwinSimulator4Params
from incubator.config.config import load_config, config_logger


def start_simulator(ok_queue=None):
    config_logger("logging.conf")
    config = load_config("startup.conf")
    simulator = PhysicalTwinSimulator4Params(rabbitmq_config=config["rabbitmq"], influxdb_config=config["influxdb"])

    simulator.setup()

    if ok_queue is not None:
        ok_queue.put("OK")

    simulator.start_serving()


if __name__ == '__main__':
    start_simulator()
