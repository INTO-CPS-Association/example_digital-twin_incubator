from config.config import config_logger, load_config
from physical_twin.controller_physical import ControllerPhysical


def start_controller_physical(ok_queue=None):
    config_logger("../logging.conf")
    config = load_config("../startup.conf")
    controller = ControllerPhysical(rabbit_config=config["rabbitmq"], **(config["physical_twin"]["controller"]))
    controller.setup()

    if ok_queue is not None:
        ok_queue.put("OK")

    controller.start_control()


if __name__ == '__main__':
    start_controller_physical()


