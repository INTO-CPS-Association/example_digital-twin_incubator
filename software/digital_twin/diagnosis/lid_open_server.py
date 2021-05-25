import logging

from influxdb_client import InfluxDBClient

from digital_twin.communication.rabbitmq_protocol import ROUTING_KEY_LIDOPEN
from digital_twin.data_access.dbmanager.incubator_data_query import query
from incubator.communication.server.rabbitmq import Rabbitmq
from incubator.communication.server.rpc_server import RPCServer
from incubator.models.plant_models.seven_parameters_model.seven_parameter_model import SevenParameterIncubatorPlant


class LidOpenServer(RPCServer):
    """
    This server exemplifies a diagnose server.
    Its behavior is similar to PlantCalibrator4Params, except that it employs the non linear optimizer to find
    the best time at which the lid was opened.
    Specifically, each time it is invoked to diagnose the lid between start and end date, it performs the following steps:
    1. Reads the data from DB according to the specified window. This includes reading the initial state from the
        KalmanFilterPlantServer data.
    2. Compares the data to the simulation with no open lid, and collects residual.
    3. Does the same for the model with open lid, and collects residual.
    4. If any of the above are below a given threshold, then it returns immediately with the appropriate reply.
    5. Otherwise, it must be the case that the lid was opened at some point.
    6. So it runs the optimization on the time at which it became open.
    7. If the optimization ends successfully, and the residual is below the threshold given, then it returns with the time at which the lid was open.
        Optionally, it can commit the results in the DB.
    """

    def __init__(self, rabbit_config, influxdb_config):
        self._l = logging.getLogger("LidOpenServer")
        self.rabbitmq = Rabbitmq(**rabbit_config)
        self.client = InfluxDBClient(**influxdb_config)
        self._influxdb_bucket = influxdb_config["bucket"]
        self._influxdb_org = influxdb_config["org"]

    def setup(self, routing_key=ROUTING_KEY_LIDOPEN, queue_name=ROUTING_KEY_LIDOPEN):
        super().setup(ROUTING_KEY_LIDOPEN, ROUTING_KEY_LIDOPEN)

    def run_diagnosis(self, diagnosis_id, start_date_ns, end_date_ns, model_params, Nevals, rtol, atol, commit, reply_fun):
        self._l.debug("Accessing database to get the data needed.")

        query_api = self.client.query_api()

        room_temp_data = query(query_api, self._influxdb_bucket, start_date_ns, end_date_ns, "low_level_driver", "t1")
        heater_data = query(query_api, self._influxdb_bucket, start_date_ns, end_date_ns, "low_level_driver",
                            "heater_on")
        average_temperature_data = query(query_api, self._influxdb_bucket, start_date_ns, end_date_ns,
                                         "low_level_driver", "average_temperature")

        heater_temperature_data = query(query_api, self._influxdb_bucket, start_date_ns, end_date_ns, "kalman_filter_plant", "T_heater")

        self._l.debug("Ensuring that we have a consistent set of samples.")
        if not (len(room_temp_data) == len(heater_data) == len(average_temperature_data) == len(heater_temperature_data)):
            error_msg = f"Inconsistent number of samples found for " \
                        f"start_date_ns={start_date_ns} and end_date_ns={end_date_ns}." \
                        f"len(room_temp_data)={len(room_temp_data)}" \
                        f"len(heater_data)={len(heater_data)}" \
                        f"len(average_temperature)={len(average_temperature_data)}" \
                        f"len(heater_temperature_data)={len(heater_temperature_data)}"
            self._l.warning(error_msg)
            return {"error": error_msg}

        self._l.debug("Checking if there are enough samples.")
        if len(room_temp_data) < 1:
            error_msg = f"Not enough physical twin data exists in the period specified " \
                        f"by start_date_ns={start_date_ns} and end_date_ns={end_date_ns}. " \
                        f"Found only {len(room_temp_data)} samples."
            self._l.warning(error_msg)
            return {"error": error_msg}

        self._l.debug("Sanitizing and converting data into lookup tables.")
        time_seconds = room_temp_data.apply(lambda row: row["_time"].timestamp(), axis=1).to_numpy()




        model = SevenParameterIncubatorPlant(**model_params)

