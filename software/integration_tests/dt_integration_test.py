import logging
import time
import unittest
from datetime import timedelta, datetime

import numpy as np
from influxdb_client import InfluxDBClient

from cli.generate_dummy_data import generate_room_data, generate_incubator_exec_data
from communication.server.rpc_client import RPCClient
from communication.shared.protocol import from_s_to_ns
from digital_twin.communication.rabbitmq_protocol import ROUTING_KEY_PLANTCALIBRATOR4
from incubator.config.config import config_logger, load_config
from digital_twin.data_access.dbmanager.incubator_data_query import query
from models.plant_models.four_parameters_model.best_parameters import four_param_model_params
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

    def test_1_basic_components(self):
        query_api = self.influxdb.query_api()

        start_date_ns = from_s_to_ns(self.start_date.timestamp())
        end_date_ns = from_s_to_ns(self.end_date.timestamp())

        room_temp_results = query(query_api, self.bucket, start_date_ns, end_date_ns, "low_level_driver", "t1")

        average_temp_results = query(query_api, self.bucket, start_date_ns, end_date_ns, "low_level_driver",
                                     "average_temperature")

        self.assertTrue(not room_temp_results.empty)
        self.assertTrue(not average_temp_results.empty)
        # Same number of samples
        self.assertEqual(room_temp_results.size, average_temp_results.size)

        self.l.info(f"Waiting for components to produce data")

        time.sleep(5)

        heater_results = query(query_api, self.bucket, start_date_ns, time.time_ns(), "controller", "heater_on")

        self.assertTrue(not heater_results.empty, "Controller did not produce results.")

        heater_temperature_results = query(query_api, self.bucket, start_date_ns, time.time_ns(), "kalman_filter_plant",
                                           "T_heater")

        self.assertTrue(not heater_temperature_results.empty, "Kalman Filter did not produce results.")

    def test_2_calibration(self):
        self.l.info(f"Running calibration")

        params = four_param_model_params

        C_air = params[0]
        G_box = params[1] + 2.0
        C_heater = params[2]
        G_heater = params[3]

        query_api = self.influxdb.query_api()

        start_date_ns = from_s_to_ns(self.start_date.timestamp())
        end_date_ns = from_s_to_ns(self.end_date.timestamp())

        room_temp_results = query(query_api, self.bucket, start_date_ns, end_date_ns, "low_level_driver", "t1")

        initial_heat_temperature = room_temp_results.iloc[0]["_value"]

        # Sharpen to start and end dates to the available data, to avoid the calibrator server complaining.
        # Using about 25% of the data should be enough.
        data_ratio = 0.25
        timespan = room_temp_results["_time"]
        start_date_ns = from_s_to_ns(timespan.iloc[-(int(data_ratio*timespan.size))].timestamp())
        end_date_ns = from_s_to_ns(timespan.iloc[-1].timestamp())
        self.l.info(f"Calibration interval: from {start_date_ns}ns to {end_date_ns}ns.")

        reply = self.client.invoke_method(ROUTING_KEY_PLANTCALIBRATOR4, "run_calibration",
                                          {
                                              "calibration_id": "integration_test_calibration",
                                              "start_date_ns": start_date_ns,
                                              "end_date_ns": end_date_ns,
                                              "Nevals": 10,
                                              "commit": False,
                                              "record_progress": True,
                                              "initial_heat_temperature": initial_heat_temperature,
                                              "initial_guess": {
                                                  "C_air": C_air,
                                                  "G_box": G_box,
                                                  "C_heater": C_heater,
                                                  "G_heater": G_heater
                                              }
                                          })
        self.assertTrue("C_air" in reply)
        self.assertTrue("G_box" in reply)
        self.assertTrue("C_heater" in reply)
        self.assertTrue("G_heater" in reply)


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

        # Time range for the fake data some past.
        # The reason we pick the past and not some interval until the present is because the data for the present is already being generated.
        # Doing so would add confusion to the test scenarios.
        cls.end_date = datetime.now() - timedelta(hours=1)
        cls.start_date = cls.end_date - timedelta(hours=10)

        cls.l.info("Connecting to influxdb.")
        cls.influxdb = InfluxDBClient(**cls.config["influxdb"])
        cls.bucket = cls.config["influxdb"]["bucket"]
        cls.org = cls.config["influxdb"]["org"]

        cls.l.info(f"Generating room temperature data between dates {cls.start_date} and {cls.end_date}.")
        points = generate_room_data(cls.influxdb, cls.bucket, cls.org, cls.start_date, cls.end_date)
        cls.l.info(f"Generated {len(points)} dummy samples of room temperature data.")

        cls.l.info("Connecting to rabbitmq.")
        cls.client = RPCClient(**(cls.config["rabbitmq"]))
        cls.client.connect_to_server()

        cls.l.info(f"Generating incubator execution data as a what-if simulation "
                   f"between dates {cls.start_date} and {cls.end_date}.")
        generate_incubator_exec_data(cls.client, cls.config, cls.start_date, cls.end_date)

        cls.l.info(f"Waiting for data to be registered by influxdb")
        time.sleep(5)

    @classmethod
    def tearDownClass(cls):
        for p in cls.processes:
            cls.l.info(f"Killing {p.name}... ")
            p.kill()
            cls.l.info("OK")

        cls.l.info(f"Closing connection to rabbitmq... ")
        cls.client.close()
        cls.client = None

        cls.l.info(f"Closing connection to influxdb... ")
        cls.influxdb.close()
        cls.influxdb = None

        stop_docker_rabbitmq()
        stop_docker_influxdb()


if __name__ == '__main__':
    unittest.main()
