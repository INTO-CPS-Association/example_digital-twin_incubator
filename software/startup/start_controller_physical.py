import logging

from physical_twin.controller_physical import ControllerPhysical

if __name__ == '__main__':
    # noinspection PyArgumentList
    logging.basicConfig(level=logging.WARN,
                        handlers=[
                            logging.FileHandler("ctrl.log"),
                            logging.StreamHandler()
                        ],
                        format='%(asctime)s.%(msecs)03d %(name)s %(levelname)s %(module)s - %(funcName)s: %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S'
                        )
    controller = ControllerPhysical(rabbitmq_ip="localhost", desired_temperature=35.0)
    controller.start_control()
