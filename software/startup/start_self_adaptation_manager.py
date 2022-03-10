from digital_twin.self_adaptation.self_adaptation_manager_server import SelfAdaptationManagerServer
from incubator.config.config import config_logger, load_config


def start_self_adaptation_manager(ok_queue=None):
    config_logger("logging.conf")
    config = load_config("startup.conf")

    self_adaptor = SelfAdaptationManagerServer(rabbit_config=config["rabbitmq"],
                                          influxdb_config=config["influxdb"],
                                          pt_config=config["physical_twin"],
                                          dt_config=config["digital_twin"])

    self_adaptor.setup()

    if ok_queue is not None:
        ok_queue.put("OK")

    self_adaptor.start()


if __name__ == '__main__':
    start_self_adaptation_manager()
