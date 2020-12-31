import logging

from influxdb_client.client.write_api import SYNCHRONOUS
from oomodelling import ModelSolver
from scipy.optimize import leastsq, least_squares

from communication.server.rpc_client import RPCClient
from communication.server.rpc_server import RPCServer
from communication.shared.connection_parameters import *
from communication.shared.protocol import from_s_to_ns, \
    ROUTING_KEY_PLANTSIMULATOR4, ROUTING_KEY_PLANTCALIBRATOR4
from digital_twin.data_access.dbmanager.data_access_parameters import INFLUXDB_TOKEN, INFLUXDB_ORG, INFLUXDB_BUCKET
from digital_twin.data_access.dbmanager.incubator_data_query import IncubatorDataQuery
from digital_twin.models.plant_models.four_parameters_model.best_parameters import four_param_model_params
from digital_twin.models.plant_models.four_parameters_model.four_parameter_model import FourParameterIncubatorPlant
from digital_twin.models.plant_models.model_functions import create_lookup_table
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
                 influx_url="http://localhost:8086",
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
        self.db = IncubatorDataQuery(url=influx_url, token=influx_token, org=influxdb_org, bucket=influxdb_bucket)

    def start_serving(self):
        super(PlantCalibrator4Params, self).start_serving(ROUTING_KEY_PLANTCALIBRATOR4, ROUTING_KEY_PLANTCALIBRATOR4)

    def on_run_calibration(self, start_date_ns, end_date_ns, Nevals):
        self._l.debug("Accessing database to get the data needed.")
        # This might look inefficient, but querying for all fields at the same time returns a list of dataframes
        # And that list does not follow the same order of the fields asked.
        # So this solution is less efficient, but more predictable.
        room_temp_data = self.db.query(start_date_ns, end_date_ns, "low_level_driver", "t1")
        heater_data = self.db.query(start_date_ns, end_date_ns, "low_level_driver", "heater_on")
        average_temperature_data = self.db.query(start_date_ns, end_date_ns, "low_level_driver", "average_temperature")

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

        with RPCClient(ip=self.ip) as client:
            def residual(params):
                self._l.debug(f"Computing residual for parameters {params}.")
                C_air = params[0]
                G_box = params[1]
                C_heater = params[2]
                G_heater = params[3]
                initial_heat_temperature = params[4]

                results = client.invoke_method(ROUTING_KEY_PLANTSIMULATOR4, "run", {"timespan_seconds": time_seconds,
                                                                                    "C_air": C_air,
                                                                                    "G_box": G_box,
                                                                                    "C_heater": C_heater,
                                                                                    "G_heater": G_heater,
                                                                                    "initial_box_temperature": average_temperature[0],
                                                                                    "initial_heat_temperature": initial_heat_temperature,
                                                                                    "room_temperature": room_temperature,
                                                                                    "heater_on": heater_on})
                assert "T" in results, results
                average_temp_approx = np.array(results["T"])
                res = average_temperature - average_temp_approx
                self._l.debug(f"Approximate cost: {sum(res**2)}.")
                return res

            initial_guess = four_param_model_params + [average_temperature[0]]

            opt_res = least_squares(residual, initial_guess, bounds=(0.0, np.inf), max_nfev=Nevals)

        self._l.debug(f"Extracting results from leastsq: {opt_res}")

        C_air = opt_res.x[0]
        G_box = opt_res.x[1]
        C_heater = opt_res.x[2]
        G_heater = opt_res.x[3]
        initial_heat_temperature = opt_res.x[4]

        msg = {
            "C_air": C_air,
            "G_box": G_box,
            "C_heater": C_heater,
            "G_heater": G_heater,
            "initial_heat_temperature": initial_heat_temperature,
            "cost": opt_res.cost,
            "nfev": opt_res.nfev
        }

        self._l.debug(f"Sending results back.")
        return msg
