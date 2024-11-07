import logging
import string
import time
import unittest
from datetime import timedelta, datetime
from multiprocessing import Process

from influxdb_client import InfluxDBClient

from cli.generate_dummy_data import generate_room_data, generate_incubator_exec_data
from incubator.communication.server.rpc_client import RPCClient
from incubator.communication.shared.protocol import from_s_to_ns
from digital_twin.communication.rabbitmq_protocol import ROUTING_KEY_PLANTCALIBRATOR4
from digital_twin.data_access.dbmanager.incubator_data_query import query
from incubator.config.config import config_logger, load_config
from incubator.tests.cli_mode_test import CLIModeTest
from incubator.models.plant_models.four_parameters_model.best_parameters import four_param_model_params
from startup.start_calibrator import start_calibrator
from startup.start_controller_physical_open_loop import start_controller_physical_open_loop
from startup.start_docker_influxdb import start_docker_influxdb, stop_docker_influxdb
from startup.start_docker_rabbitmq import start_docker_rabbitmq, stop_docker_rabbitmq
from startup.start_incubator_realtime_mockup import start_incubator_realtime_mockup
from startup.start_influx_data_recorder import start_influx_data_recorder
from startup.start_low_level_driver_mockup import start_low_level_driver_mockup
from startup.start_plant_kalmanfilter import start_plant_kalmanfilter
from startup.start_plant_simulator import start_plant_simulator
from startup.start_self_adaptation_manager import start_self_adaptation_manager
from startup.start_simulator import start_simulator
from startup.utils.db_tasks import setup_db
from startup.utils.start_as_daemon import start_as_daemon


# TODO: Create a second integration test, just like this one, but that uses the open loop controller consistently.
#  Right now, we're using the open loop controller online, but the closed loop controller to generate the dummy data.
class StartDTWithDummyData(CLIModeTest):
    """
    The tests in this class are supported to run in alphabetical order, so that, e.g.,
        the first test can produce dummy data, which the following tests use.
    """

    processes: list[Process] = None
    l: logging.Logger = None
    end_date: datetime = None
    start_date: datetime = None
    config: dict = None
    influxdb: InfluxDBClient = None
    bucket: string = None
    org: string = None
    client: RPCClient = None
    WAIT_FOR_DB = 2  # seconds

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
        # cls.processes.append(start_as_daemon(start_controller_physical))
        cls.processes.append(start_as_daemon(start_controller_physical_open_loop))
        cls.processes.append(start_as_daemon(start_self_adaptation_manager))

        config_logger("logging.conf")
        cls.config = load_config("startup.conf")

        cls.l = logging.getLogger("DTIntegrationTest")

        # Time range for the fake data some past. The reason we pick the past and not some interval until the present
        # is because the data for the present is already being generated. Doing so would add confusion to the test
        # scenarios.
        cls.end_date = datetime.now() - timedelta(hours=1)
        cls.start_date = cls.end_date - timedelta(hours=4)

        cls.l.info("Connecting to influxdb.")
        cls.influxdb = InfluxDBClient(**cls.config["influxdb"])
        cls.bucket = cls.config["influxdb"]["bucket"]
        cls.org = cls.config["influxdb"]["org"]

        cls.l.info(f"Generating room temperature data between dates {cls.start_date} and {cls.end_date}.")
        points = generate_room_data(cls.influxdb, cls.bucket, cls.org, cls.start_date, cls.end_date)
        number_room_data_points = len(points)
        cls.l.info(f"Generated {number_room_data_points} dummy samples of room temperature data.")

        cls.l.info(f"Waiting for influxdb to register data")
        time.sleep(cls.WAIT_FOR_DB)

        query_api = cls.influxdb.query_api()
        start_date_ns = from_s_to_ns(cls.start_date.timestamp())
        # Add one to make influxdb include the stop date.
        # See https://github.com/INTO-CPS-Association/example_digital-twin_incubator/issues/20
        end_date_ns = from_s_to_ns(cls.end_date.timestamp()) + 1
        room_temp_results = query(query_api, cls.bucket, start_date_ns, end_date_ns, "low_level_driver", "t3")

        number_room_data_points_registered_influxdb = len(room_temp_results["_time"])
        cls.l.debug(
            f"InfluxDB registered {number_room_data_points_registered_influxdb} dummy samples of room temperature data.")

        assert number_room_data_points == number_room_data_points_registered_influxdb

        cls.l.info("Connecting to rabbitmq.")
        cls.client = RPCClient(**(cls.config["rabbitmq"]))
        cls.client.connect_to_server()

        cls.l.info(f"Generating incubator execution data as a what-if simulation "
                   f"between dates {cls.start_date} and {cls.end_date}.")
        generated_data = generate_incubator_exec_data(cls.client, cls.config, cls.start_date, cls.end_date)
        number_points_pt_simulation = len(generated_data)
        cls.l.debug(f"Generated {number_points_pt_simulation} samples from what-if simulation.")

        cls.l.info(f"Waiting for influxdb to register data")
        time.sleep(cls.WAIT_FOR_DB)

    def test_1_basic_components(self):
        query_api = self.influxdb.query_api()

        start_date_ns = from_s_to_ns(self.start_date.timestamp())
        end_date_ns = from_s_to_ns(self.end_date.timestamp()) + 1  # Add one to make influxdb include the stop date.

        room_temp_results = query(query_api, self.bucket, start_date_ns, end_date_ns, "low_level_driver", "t3")

        average_temp_results = query(query_api, self.bucket, start_date_ns, end_date_ns, "low_level_driver",
                                     "average_temperature")

        self.assertTrue(not room_temp_results.empty)
        self.assertTrue(not average_temp_results.empty)
        # Same number of samples.
        # Commented out as it's very brittle.
        # self.assertEqual(len(room_temp_results), len(average_temp_results))

        self.l.info(f"Waiting for components to produce data")
        time.sleep(self.WAIT_FOR_DB + 4)

        heater_results = query(query_api, self.bucket, start_date_ns, time.time_ns(), "controller", "heater_on")

        self.assertTrue(not heater_results.empty, "Controller did not produce results.")

        heater_temperature_results = query(query_api, self.bucket, start_date_ns, time.time_ns(), "kalman_filter_plant",
                                           "T_heater")

        self.assertTrue(not heater_temperature_results.empty, "Kalman Filter did not produce results.")

    def test_2_calibration(self):
        self.l.info(f"Running calibration")

        params = {}
        params_plant = self.config["digital_twin"]["models"]["plant"]["param4"]
        for k in params_plant:
            params[k] = params_plant[k]

        # Cause small disturbance in parameters just to make the calibration interesting.
        params["G_box"] += 0.0

        query_api = self.influxdb.query_api()

        start_date_ns = from_s_to_ns(self.start_date.timestamp())
        end_date_ns = from_s_to_ns(self.end_date.timestamp()) + 1  # Add one to make influxdb include the stop date.

        room_temp_results = query(query_api, self.bucket, start_date_ns, end_date_ns, "low_level_driver", "t3")

        initial_heat_temperature = room_temp_results.iloc[0]["t3"]

        # Sharpen to start and end dates to the available data, to avoid the calibrator server complaining.
        # Using about 25% of the data should be enough.
        data_ratio = 1.0
        timespan = room_temp_results["_time"]
        start_date_ns = from_s_to_ns(timespan.iloc[-(int(data_ratio * timespan.size))].timestamp())
        end_date_ns = from_s_to_ns(timespan.iloc[-1].timestamp())
        self.l.info(f"Calibration interval: from {start_date_ns}ns to {end_date_ns}ns.")

        reply = self.client.invoke_method(ROUTING_KEY_PLANTCALIBRATOR4, "run_calibration",
                                          {
                                              "calibration_id": "integration_test_calibration",
                                              "start_date_ns": start_date_ns,
                                              "end_date_ns": end_date_ns,
                                              "Nevals": 1,
                                              "commit": True,
                                              "record_progress": True,
                                              "initial_heat_temperature": initial_heat_temperature,
                                              "initial_guess": params
                                          })
        self.assertTrue("C_air" in reply)
        self.assertTrue("G_box" in reply)
        self.assertTrue("C_heater" in reply)
        self.assertTrue("G_heater" in reply)
        self.assertTrue("V_heater" in reply)
        self.assertTrue("I_heater" in reply)

        self.assertAlmostEqual(params_plant["C_air"], reply["C_air"], places=3)
        self.assertAlmostEqual(params_plant["G_box"], reply["G_box"], places=3)
        self.assertAlmostEqual(params_plant["C_heater"], reply["C_heater"], places=3)
        self.assertAlmostEqual(params_plant["G_heater"], reply["G_heater"], places=3)
        self.assertAlmostEqual(params_plant["V_heater"], reply["V_heater"], places=3)
        self.assertAlmostEqual(params_plant["I_heater"], reply["I_heater"], places=3)

    @classmethod
    def tearDownClass(cls):
        for p in cls.processes:
            cls.l.info(f"Killing {p.name}... ")
            p.kill()
            cls.l.info("OK")

        cls.l.info(f"Closing connection to rabbitmq... ")
        cls.client.close()

        cls.l.info(f"Closing connection to influxdb... ")
        cls.influxdb.close()

        stop_docker_rabbitmq()
        stop_docker_influxdb()


if __name__ == '__main__':
    unittest.main()
