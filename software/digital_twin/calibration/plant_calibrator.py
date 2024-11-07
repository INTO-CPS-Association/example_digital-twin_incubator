import logging

from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS
from scipy.optimize import least_squares

from digital_twin.communication.rabbitmq_protocol import ROUTING_KEY_PLANTCALIBRATOR4, ROUTING_KEY_PLANTSIMULATOR4
from digital_twin.data_access.dbmanager.incubator_data_query import query_convert_aligned_data
import numpy as np

from incubator.communication.server.rpc_client import RPCClient
from incubator.communication.server.rpc_server import RPCServer


class PlantCalibrator4Params(RPCServer):
    """
    Can run calibrations of the plant pt_simulator.
    """

    def __init__(self, rabbitmq_config, influxdb_config):
        super().__init__(**rabbitmq_config)
        self.rabbitmq_config = rabbitmq_config
        self._l = logging.getLogger("PlantCalibrator4Params")
        self.client = InfluxDBClient(**influxdb_config)
        self._influxdb_bucket = influxdb_config["bucket"]
        self._influxdb_org = influxdb_config["org"]
        self.nevals = 0

    def setup(self, routing_key=ROUTING_KEY_PLANTCALIBRATOR4, queue_name=ROUTING_KEY_PLANTCALIBRATOR4):
        super(PlantCalibrator4Params, self).setup(ROUTING_KEY_PLANTCALIBRATOR4, ROUTING_KEY_PLANTCALIBRATOR4)

    def run_calibration(self, calibration_id, start_date_ns, end_date_ns, Nevals, commit, record_progress,
                        initial_heat_temperature, initial_guess, reply_fun):
        self._l.debug("Accessing database to get the data needed.")
        # This might look inefficient, but querying for all fields at the same time returns a list of dataframes
        # And that list does not follow the same order of the fields asked.
        # So this solution is less efficient, but more predictable.
        query_api = self.client.query_api()

        time_seconds, results = query_convert_aligned_data(query_api, self._influxdb_bucket, start_date_ns, end_date_ns,
                                                           {
                                                               "low_level_driver": ["t3", "heater_on",
                                                                                    "average_temperature"]
                                                           })

        room_temp_data = results["low_level_driver"]["t3"]
        heater_data = results["low_level_driver"]["heater_on"]
        average_temperature = results["low_level_driver"]["average_temperature"]

        self._l.debug("Converting data to lists.")
        room_temperature = room_temp_data.tolist()
        heater_on = heater_data.tolist()
        time_seconds_list = list(time_seconds)

        with RPCClient(**self.rabbitmq_config) as rpc_client:
            self.nevals = 0

            def residual(params):
                self._l.debug(f"Computing residual for parameters {params}.")
                C_air = params[0]
                G_box = params[1]
                C_heater = params[2]
                G_heater = params[3]
                V_heater = params[4]
                I_heater = params[5]
                results = rpc_client.invoke_method(ROUTING_KEY_PLANTSIMULATOR4, "run",
                                                   {
                                                       "tags": {
                                                           "calibration": calibration_id,
                                                           "attempt": self.nevals
                                                       },
                                                       "timespan_seconds": time_seconds_list,
                                                       "C_air": C_air,
                                                       "G_box": G_box,
                                                       "C_heater": C_heater,
                                                       "G_heater": G_heater,
                                                       "V_heater": V_heater,
                                                       "I_heater": I_heater,
                                                       "initial_box_temperature": average_temperature[0],
                                                       "initial_heat_temperature": initial_heat_temperature,
                                                       "room_temperature": room_temperature,
                                                       "heater_on": heater_on,
                                                       "record": record_progress
                                                   })
                assert "average_temperature" in results, results
                average_temp_approx = np.array(results["average_temperature"])
                res = average_temperature - average_temp_approx
                self._l.debug(f"Approximate cost: {sum(res ** 2)}.")
                self.nevals += 1
                return res

            initial_guess_array = [
                initial_guess["C_air"],
                initial_guess["G_box"],
                initial_guess["C_heater"],
                initial_guess["G_heater"],
                initial_guess["V_heater"],
                initial_guess["I_heater"]
            ]

            opt_res = least_squares(residual, initial_guess_array, bounds=(0.0, np.inf), max_nfev=Nevals)

        self._l.debug(f"Extracting results from leastsq: {opt_res}")

        C_air = opt_res.x[0]
        G_box = opt_res.x[1]
        C_heater = opt_res.x[2]
        G_heater = opt_res.x[3]
        V_heater = opt_res.x[4]
        I_heater = opt_res.x[5]

        msg = {
            "C_air": C_air,
            "G_box": G_box,
            "C_heater": C_heater,
            "G_heater": G_heater,
            "V_heater": V_heater,
            "I_heater": I_heater,
            "cost": opt_res.cost,
            "nfev": opt_res.nfev
        }

        if commit:
            self._l.debug(f"Sending results to database.")
            point = {
                "measurement": "plant_calibrator",
                "time": start_date_ns,
                "tags": {
                    "source": "plant_calibrator",
                    "experiment": calibration_id,
                    "variability": "parameter"
                },
                "fields": msg
            }
            write_api = self.client.write_api(write_options=SYNCHRONOUS)
            write_api.write(self._influxdb_bucket, self._influxdb_org, point)

        self._l.debug(f"Sending results back.")
        reply_fun(msg)
