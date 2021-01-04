import logging

from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS
from scipy.optimize import least_squares

from communication.server.rpc_client import RPCClient
from communication.server.rpc_server import RPCServer
from communication.shared.connection_parameters import *
from communication.shared.protocol import ROUTING_KEY_PLANTSIMULATOR4, ROUTING_KEY_PLANTCALIBRATOR4
from digital_twin.data_access.dbmanager.data_access_parameters import INFLUXDB_TOKEN, INFLUXDB_ORG, INFLUXDB_BUCKET, \
    INFLUXDB_URL
from digital_twin.data_access.dbmanager.incubator_data_query import query
import numpy as np


class PlantCalibrator4Params(RPCServer):
    """
    Can run calibrations of the plant simulator.
    """

    def __init__(self, ip=RASPBERRY_IP,
                 port=RASPBERRY_PORT,
                 username=PIKA_USERNAME,
                 password=PIKA_PASSWORD,
                 vhost=PIKA_VHOST,
                 exchange_name=PIKA_EXCHANGE,
                 exchange_type=PIKA_EXCHANGE_TYPE,
                 influx_url=INFLUXDB_URL,
                 influx_token=INFLUXDB_TOKEN,
                 influxdb_org=INFLUXDB_ORG,
                 influxdb_bucket=INFLUXDB_BUCKET
                 ):
        super().__init__(ip=ip,
                         port=port,
                         username=username,
                         password=password,
                         vhost=vhost,
                         exchange_name=exchange_name,
                         exchange_type=exchange_type)
        self._l = logging.getLogger("PlantCalibrator")
        self.client = InfluxDBClient(url=influx_url, token=influx_token, org=influxdb_org)
        self._influxdb_bucket = influxdb_bucket
        self._influxdb_org = influxdb_org
        self.nevals = 0

    def start_serving(self):
        super(PlantCalibrator4Params, self).start_serving(ROUTING_KEY_PLANTCALIBRATOR4, ROUTING_KEY_PLANTCALIBRATOR4)

    def run_calibration(self, calibration_id, start_date_ns, end_date_ns, Nevals, commit, record_progress,
                        initial_heat_temperature, initial_guess):
        self._l.debug("Accessing database to get the data needed.")
        # This might look inefficient, but querying for all fields at the same time returns a list of dataframes
        # And that list does not follow the same order of the fields asked.
        # So this solution is less efficient, but more predictable.
        query_api = self.client.query_api()
        room_temp_data = query(query_api, self._influxdb_bucket, start_date_ns, end_date_ns, "low_level_driver", "t1")
        heater_data = query(query_api, self._influxdb_bucket, start_date_ns, end_date_ns, "low_level_driver",
                            "heater_on")
        average_temperature_data = query(query_api, self._influxdb_bucket, start_date_ns, end_date_ns,
                                         "low_level_driver", "average_temperature")

        self._l.debug("Accessing database to get the most recent parameters.")

        self._l.debug("Ensuring that we have a consistent set of samples.")
        if not (len(room_temp_data) == len(heater_data) == len(average_temperature_data)):
            error_msg = f"Inconsistent number of samples found for " \
                        f"start_date_ns={start_date_ns} and end_date_ns={end_date_ns}." \
                        f"len(room_temp_data)={len(room_temp_data)}" \
                        f"len(heater_data)={len(heater_data)}" \
                        f"len(average_temperature)={len(average_temperature_data)}"
            self._l.warning(error_msg)
            return {"error": error_msg}

        self._l.debug("Checking if there are enough samples.")
        if len(room_temp_data) < 1:
            error_msg = f"Not enough physical twin data exists in the period specified " \
                        f"by start_date_ns={start_date_ns} and end_date_ns={end_date_ns}. Found only {len(room_temp_data)} samples."
            self._l.warning(error_msg)
            return {"error": error_msg}

        self._l.debug("Converting data to lists and time to seconds.")
        time_seconds = room_temp_data.apply(lambda row: row["_time"].timestamp(), axis=1).to_numpy().tolist()
        room_temperature = room_temp_data["_value"].to_numpy().tolist()
        average_temperature = average_temperature_data["_value"].to_numpy()
        heater_on = heater_data["_value"].to_numpy().tolist()

        with RPCClient(ip=self.ip) as rpc_client:
            self.nevals = 0

            def residual(params):
                self._l.debug(f"Computing residual for parameters {params}.")
                C_air = params[0]
                G_box = params[1]
                C_heater = params[2]
                G_heater = params[3]
                results = rpc_client.invoke_method(ROUTING_KEY_PLANTSIMULATOR4, "run",
                                                   {
                                                       "tags": {
                                                           "calibration": calibration_id,
                                                           "attempt": self.nevals
                                                       },
                                                       "timespan_seconds": time_seconds,
                                                       "C_air": C_air,
                                                       "G_box": G_box,
                                                       "C_heater": C_heater,
                                                       "G_heater": G_heater,
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
                initial_guess["G_heater"]
            ]

            opt_res = least_squares(residual, initial_guess_array, bounds=(0.0, np.inf), max_nfev=Nevals)

        self._l.debug(f"Extracting results from leastsq: {opt_res}")

        C_air = opt_res.x[0]
        G_box = opt_res.x[1]
        C_heater = opt_res.x[2]
        G_heater = opt_res.x[3]

        msg = {
            "C_air": C_air,
            "G_box": G_box,
            "C_heater": C_heater,
            "G_heater": G_heater,
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
        return msg
