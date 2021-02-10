import logging
import unittest
from datetime import timedelta, datetime

from influxdb_client import InfluxDBClient

from cli.generate_dummy_data import generate_room_data, generate_incubator_exec_data
from communication.shared.protocol import from_s_to_ns
from incubator.config.config import config_logger, load_config
from digital_twin.data_access.dbmanager.incubator_data_query import query
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
from incubator.tests.cli_mode_test import CLIModeTest


class StartDTWithDummyData(CLIModeTest):
    """
    The tests in this class are supported to run in alphabetical order, so that, e.g.,
        the first test can produce dummy data, which the following tests use.
    """

    def test_1_dummy_data(self):
        dbclient = InfluxDBClient(**self.config["influxdb"])
        query_api = dbclient.query_api()
        bucket = self.config["influxdb"]["bucket"]

        start_date_ns = from_s_to_ns(self.start_date.timestamp())
        end_date_ns = from_s_to_ns(self.end_date.timestamp())

        room_temp_results = query(query_api, bucket, start_date_ns, end_date_ns, "low_level_driver", "t1")

        average_temp_results = query(query_api, bucket, start_date_ns, end_date_ns, "low_level_driver", "average_temperature")

        self.assertTrue(not room_temp_results.empty)
        self.assertTrue(not average_temp_results.empty)
        # Same number of samples
        self.assertEqual(room_temp_results.size, average_temp_results.size)

    def test_2_basic_components(self):
        # TODO: Check that controller physical is producing data.
        pass

    @classmethod
    def setUpClass(cls):
        stop_docker_influxdb()
        stop_docker_rabbitmq()
        setup_db(influxdb_docker_dir="digital_twin/data_access/influxdbserver")
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

        config_logger("logging.conf")
        cls.config = load_config("startup.conf")

        cls.l = logging.getLogger("DTIntegrationTest")

        # Time range for the fake data for 10h ago
        cls.end_date = datetime.now()
        cls.start_date = cls.end_date - timedelta(hours=10)

        cls.l.info(f"Generating room temperature data between dates {cls.start_date} and {cls.end_date}.")
        generate_room_data(cls.config["influxdb"], cls.start_date, cls.end_date)

        cls.l.info(f"Generating incubator execution data as a what-if simulation "
                   f"between dates {cls.start_date} and {cls.end_date}.")
        generate_incubator_exec_data(cls.config, cls.start_date, cls.end_date)

    @classmethod
    def tearDownClass(cls):
        for p in cls.processes:
            cls.l.info(f"Killing {p.name}... ")
            p.kill()
            cls.l.info("OK")
        stop_docker_rabbitmq()
        stop_docker_influxdb()

if __name__ == '__main__':
    unittest.main()
