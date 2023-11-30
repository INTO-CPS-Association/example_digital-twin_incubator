from digital_twin.monitoring.energy_saver_server import EnergySaverServer
from incubator.config.config import config_logger, load_config
from incubator.physical_twin.low_level_driver_server import CTRL_EXEC_INTERVAL


def start_energy_saver(ok_queue=None):
    config_logger("logging.conf")
    config = load_config("startup.conf")

    monitor = EnergySaverServer(4.0, config["physical_twin"]["controller"], config["rabbitmq"])

    monitor.setup()

    if ok_queue is not None:
        ok_queue.put("OK")

    monitor.start_monitoring()


if __name__ == '__main__':
    start_energy_saver()
