import logging

from influxdb_client import InfluxDBClient
from oomodelling import ModelSolver
from scipy.optimize import least_squares

from communication.shared.protocol import from_s_to_ns, from_s_to_ns_array
from digital_twin.communication.rabbitmq_protocol import ROUTING_KEY_LIDOPEN
from digital_twin.data_access.dbmanager.incubator_data_query import query, query_convert_aligned_data
from incubator.communication.server.rabbitmq import Rabbitmq
from incubator.communication.server.rpc_server import RPCServer
from incubator.models.plant_models.seven_parameters_model.seven_parameter_model import SevenParameterIncubatorPlant
from models.plant_models.model_functions import create_lookup_table
import numpy as np


def compute_simulation_lid_residual(time_seconds, model_params, heater_data, room_temp_data,
                                    average_temperature_data, lid_open_data):
    model = SevenParameterIncubatorPlant(**model_params)
    in_heater_table = create_lookup_table(time_seconds, heater_data)
    in_room_temperature = create_lookup_table(time_seconds, room_temp_data)
    lid_open = create_lookup_table(time_seconds, lid_open_data)
    model.in_heater_on = lambda: in_heater_table(model.time())
    model.in_room_temperature = lambda: in_room_temperature(model.time())
    model.in_lid_open = lambda: lid_open(model.time())

    t0 = time_seconds[0]
    tf = time_seconds[-1]
    h = (tf - t0) / len(time_seconds)
    sol = ModelSolver().simulate(model, t0, tf, h, t_eval=time_seconds)

    average_temp_approx = sol.y[0, :]
    residual = (average_temperature_data - average_temp_approx)

    return residual


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
    6. So it runs the optimization on the times at which it became open/closed.
        Note that in general, in order to achieve this, multiple optimizations are needed, because the lid may be opened and closed multiple times.
        We would start with the assumption that it was opened/closed at least once, and then proceed to increase the number of openings and closings.
        This may not terminate, and knowing at least how many times the lid was opened/closed would be helpful.
    7. If the optimization ends successfully, and the residual is below the threshold given, then it returns with the signal of the lid opening/closing.
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

    def run_diagnosis(self, diagnosis_id, start_date_ns, end_date_ns, model_params, Nevals, rtol, atol, commit,
                      reply_fun):
        self._l.debug("Accessing database to get the data needed.")

        query_api = self.client.query_api()

        time_seconds, results = query_convert_aligned_data(query_api, self._influxdb_bucket, start_date_ns, end_date_ns,
                                                           {
                                                               "low_level_driver": ["t1", "heater_on",
                                                                                    "average_temperature"],
                                                               "kalman_filter_plant": ["T_heater"]
                                                           })

        room_temp_data = results["low_level_driver"]["t1"]
        heater_data = results["low_level_driver"]["heater_on"]
        average_temperature_data = results["low_level_driver"]["average_temperature"]
        heater_temperature_data = results["kalman_filter_plant"]["T_heater"]

        self._l.debug("Defining initial conditions.")
        assert "initial_room_temperature" not in model_params
        assert "initial_box_temperature" not in model_params
        assert "initial_heat_temperature" not in model_params
        model_params["initial_room_temperature"] = room_temp_data[0]
        model_params["initial_box_temperature"] = average_temperature_data[0]
        model_params["initial_heat_temperature"] = heater_temperature_data[0]

        time_ns = list(from_s_to_ns_array(time_seconds))

        self._l.debug("Running simulation with closed lid.")
        lid_open_data = np.zeros_like(time_seconds)
        lid_closed_residual = compute_simulation_lid_residual(time_seconds, model_params, heater_data, room_temp_data,
                                                              average_temperature_data, lid_open_data)
        lid_closed_good_enough = np.isclose(np.sum(lid_closed_residual ** 2), 0, rtol, atol)

        self._l.debug(f"lid_closed_good_enough={lid_closed_good_enough}")

        if lid_closed_good_enough:
            msg = {"lid_open_data": list(lid_open_data),
                   "time": time_ns}
            reply_fun(msg)
            return

        self._l.debug("Running simulation with open lid.")

        lid_open_data = np.ones_like(time_seconds)
        lid_open_residual = compute_simulation_lid_residual(time_seconds, model_params, heater_data, room_temp_data,
                                                            average_temperature_data, lid_open_data)
        lid_open_good_enough = np.isclose(np.sum(lid_open_residual ** 2), 0, rtol, atol)

        self._l.debug(f"lid_open_good_enough={lid_open_good_enough}")

        if lid_open_good_enough:
            msg = {"lid_open_data": list(lid_open_data),
                   "time": time_ns}
            reply_fun(msg)
            return

        self._l.debug("Diagnosing time of lid opening.")

        def residual(params):
            t_open = params[0]
            lid_open_data = np.array([0.0 if t < t_open else 1.0 for t in time_seconds])
            res = compute_simulation_lid_residual(time_seconds, model_params, heater_data, room_temp_data,
                                                  average_temperature_data, lid_open_data)
            self._l.debug(f"cost({t_open})={np.sum(res ** 2)}")
            return res

        opt_res = least_squares(residual, [(time_seconds[-1] - time_seconds[0]) / 2.0],
                                bounds=(time_seconds[0], time_seconds[-1]), max_nfev=Nevals)

        self._l.debug(f"results={opt_res}")

        res_good_enough = np.isclose(opt_res.cost, 0, rtol, atol)

        self._l.debug(f"res_good_enough={res_good_enough}")
        if res_good_enough:
            t_open = opt_res.x[0]
            lid_open_data = np.array([0.0 if t < t_open else 1.0 for t in time_seconds])
            msg = {"lid_open_data": list(lid_open_data),
                   "time": time_ns}
            reply_fun(msg)
            return

        self._l.debug("Diagnosing time of lid closing.")

        def residual(params):
            t_close = params[0]
            lid_open_data = np.array([1.0 if t < t_close else 0.0 for t in time_seconds])
            res = compute_simulation_lid_residual(time_seconds, model_params, heater_data, room_temp_data,
                                                  average_temperature_data, lid_open_data)
            self._l.debug(f"cost({t_close})={np.sum(res ** 2)}")
            return res

        opt_res = least_squares(residual, [(time_seconds[-1] - time_seconds[0]) / 2.0],
                                bounds=(time_seconds[0], time_seconds[-1]), max_nfev=Nevals)

        self._l.debug(f"results={opt_res}")

        res_good_enough = np.isclose(opt_res.cost, 0, rtol, atol)

        self._l.debug(f"res_good_enough={res_good_enough}")
        if res_good_enough:
            t_close = opt_res.x[0]
            lid_open_data = np.array([1.0 if t < t_close else 0.0 for t in time_seconds])
            msg = {"lid_open_data": list(lid_open_data),
                   "time": time_ns}
            reply_fun(msg)
            return

        self._l.warning("None of the diagnosis methods worked.")
        msg = {"Error": "None of the diagnosis methods worked."}
        reply_fun(msg)
        return
