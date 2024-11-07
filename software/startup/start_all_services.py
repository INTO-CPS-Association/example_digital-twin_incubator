from startup.utils.start_as_daemon import start_as_daemon
from startup.start_docker_influxdb import start_docker_influxdb
from startup.start_influx_data_recorder import start_influx_data_recorder

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
    # start_as_daemon(start_controller_from_kyx)

    # Enable self adaptation
    # start_as_daemon(start_self_adaptation_manager)
    # start_as_daemon(start_supervisor)
    # start_as_daemon(start_energy_saver)
