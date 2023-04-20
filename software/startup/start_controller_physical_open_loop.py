from incubator.config.config import config_logger, load_config
from incubator.physical_twin.controller_physical_openloop import ControllerPhysicalOpenLoop


def start_controller_physical_open_loop(ok_queue=None):
    config_logger("logging.conf")
    config = load_config("startup.conf")
    controller = ControllerPhysicalOpenLoop(rabbit_config=config["rabbitmq"], **(config["physical_twin"]["controller_open_loop"]))
    controller.setup()

    if ok_queue is not None:
        ok_queue.put("OK")

    controller.start_control()


if __name__ == '__main__':
    start_controller_physical_open_loop()


