from physical_twin.controller_physical import ControllerPhysical

if __name__ == '__main__':
    controller = ControllerPhysical(rabbitmq_ip="localhost", desired_temperature=35.0)
    controller.start_control()