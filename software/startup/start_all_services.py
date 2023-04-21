from startup.start_calibrator import start_calibrator
from startup.start_controller_physical_open_loop import start_controller_physical_open_loop
from startup.start_plant_kalmanfilter import start_plant_kalmanfilter
from startup.start_plant_simulator import start_plant_simulator
from startup.start_self_adaptation_manager import start_self_adaptation_manager
from startup.start_simulator import start_simulator
from startup.start_controller_physical import start_controller_physical
from startup.start_docker_influxdb import start_docker_influxdb
from startup.start_docker_rabbitmq import start_docker_rabbitmq
from startup.start_incubator_realtime_mockup import start_incubator_realtime_mockup
from startup.start_influx_data_recorder import start_influx_data_recorder
from startup.start_low_level_driver_mockup import start_low_level_driver_mockup
from startup.start_supervisor import start_supervisor
from startup.utils.start_as_daemon import start_as_daemon

if __name__ == '__main__':
    # start_docker_rabbitmq()
    start_docker_influxdb()

    # start_as_daemon(start_incubator_realtime_mockup)
    # start_as_daemon(start_low_level_driver_mockup)
    start_as_daemon(start_influx_data_recorder)
    # start_as_daemon(start_plant_kalmanfilter)

    # start_as_daemon(start_plant_simulator)
    # start_as_daemon(start_simulator)
    # start_as_daemon(start_calibrator)

    # Choose one of the controllers below:
    # start_as_daemon(start_controller_physical)
    # start_as_daemon(start_controller_physical_open_loop)

    # Enable self adaptation
    # start_as_daemon(start_self_adaptation_manager)
    # start_as_daemon(start_supervisor)

