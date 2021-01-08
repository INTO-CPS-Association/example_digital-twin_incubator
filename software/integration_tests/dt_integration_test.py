import unittest
from time import sleep

from cli.generate_dummy_data import generate_dummy_data
from startup.start_calibrator import start_calibrator
from startup.start_plant_kalmanfilter import start_plant_kalmanfilter
from startup.start_plant_simulator import start_plant_simulator
from startup.start_simulator import start_simulator
from startup.start_controller_physical import start_controller_physical
from startup.start_docker_influxdb import start_docker_influxdb, stop_docker_influxdb
from startup.start_docker_rabbitmq import start_docker_rabbitmq, stop_docker_rabbitmq
from startup.start_incubator_realtime_mockup import start_incubator_realtime_mockup
from startup.start_influx_data_recorder import start_influx_data_recorder
from startup.start_low_level_driver_mockup import start_low_level_driver_mockup
from startup.utils.db_tasks import setup_db
from startup.utils.start_as_daemon import start_as_daemon
from tests.cli_mode_test import CLIModeTest


class StartDTWithDummyData(CLIModeTest):

    @classmethod
    def setUpClass(cls):
        setup_db(influxdb_docker_dir="../digital_twin/data_access/influxdbserver")
        start_docker_rabbitmq()
        start_docker_influxdb()
        cls.processes = []
        cls.processes.append(start_as_daemon(start_simulator))
        cls.processes.append(start_as_daemon(start_incubator_realtime_mockup))
        cls.processes.append(start_as_daemon(start_low_level_driver_mockup))
        cls.processes.append(start_as_daemon(start_influx_data_recorder))
        cls.processes.append(start_as_daemon(start_plant_kalmanfilter))
        cls.processes.append(start_as_daemon(start_plant_simulator))
        cls.processes.append(start_as_daemon(start_calibrator))
        cls.processes.append(start_as_daemon(start_controller_physical))

        print("Populating DB... ", end="")
        generate_dummy_data()
        print("OK")


    @classmethod
    def tearDownClass(cls):
        for p in cls.processes:
            print(f"Killing {p.name}... ", end="")
            p.kill()
            print("OK")
        stop_docker_rabbitmq()
        stop_docker_influxdb()

    def test_populate_dummy_data(self):
        sleep(2.0)


if __name__ == '__main__':
    unittest.main()
