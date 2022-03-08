from digital_twin.self_adaptation.self_adaptation_manager_server import SelfAdaptationManagerServer
from incubator.config.config import config_logger, load_config


def start_self_adaptation_simulator(ok_queue=None):
    config_logger("logging.conf")
    config = load_config("startup.conf")

    monitor = SelfAdaptationManagerServer(rabbit_config=config["rabbitmq"])

    monitor.setup()

    if ok_queue is not None:
        ok_queue.put("OK")

    monitor.start()


if __name__ == '__main__':
    start_self_adaptation_simulator()
