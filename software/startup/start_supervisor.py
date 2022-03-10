from digital_twin.self_adaptation.supervisor_server import SupervisorServer
from incubator.config.config import config_logger, load_config


def start_supervisor(ok_queue=None):
    config_logger("logging.conf")
    config = load_config("startup.conf")

    supervisor = SupervisorServer(rabbit_config=config["rabbitmq"],
                                          influxdb_config=config["influxdb"],
                                          pt_config=config["physical_twin"],
                                          dt_config=config["digital_twin"])

    supervisor.setup()

    if ok_queue is not None:
        ok_queue.put("OK")

    supervisor.start()


if __name__ == '__main__':
    start_supervisor()
