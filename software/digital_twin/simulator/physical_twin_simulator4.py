import logging

import numpy as np
from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS
from oomodelling import ModelSolver

from digital_twin.communication.rabbitmq_protocol import ROUTING_KEY_PTSIMULATOR4
from digital_twin.data_access.dbmanager.incubator_data_conversion import convert_to_results_db
from digital_twin.data_access.dbmanager.incubator_data_query import query_convert_aligned_data
from incubator.communication.server.rpc_server import RPCServer
from incubator.communication.shared.protocol import from_ns_to_s
from incubator.models.physical_twin_models.system_model4 import SystemModel4Parameters
from incubator.models.plant_models.model_functions import create_lookup_table


class PhysicalTwinSimulator4ParamsServer(RPCServer):
    """
    Can run simulations of the physical twin. This includes controller and plant.
    """

    def __init__(self, rabbitmq_config, influxdb_config):
        super().__init__(**rabbitmq_config)
        self._l = logging.getLogger("PhysicalTwinSimulator4ParamsServer")
        self.client = InfluxDBClient(**influxdb_config)
        self._influxdb_bucket = influxdb_config["bucket"]
        self._influxdb_org = influxdb_config["org"]

    def setup(self):
        super(PhysicalTwinSimulator4ParamsServer, self).setup(ROUTING_KEY_PTSIMULATOR4, ROUTING_KEY_PTSIMULATOR4)

    def run_historical(self, start_date, end_date,
                       C_air,
                       G_box,
                       C_heater,
                       G_heater, V_heater, I_heater,
                       lower_bound, heating_time, heating_gap, temperature_desired,
                       controller_comm_step,
                       initial_box_temperature,
                       initial_heat_temperature,
                       record,
                       as_lld,
                       reply_fun):
        # Access database to get the data needed.
        query_api = self.client.query_api()

        # Adds one to end_data to ensure that points coinciding with final end data are also captured.
        # See https://github.com/INTO-CPS-Association/example_digital-twin_incubator/issues/20
        time_seconds, results = query_convert_aligned_data(query_api, self._influxdb_bucket, start_date, end_date + 1, {
            "low_level_driver": ["t3"]
        })

        # Ensure that the start_date and end_date are in the lookup table.
        # We need to do this because the data in the database may not exist at exactly these dates.
        # So we need to interpolate it from the data that exists.
        room_temperature = results["low_level_driver"]["t3"]
        original_len = len(room_temperature)
        room_temperature_for_lookup = np.append(np.insert(room_temperature, 0, room_temperature[0]), room_temperature[-1])

        assert len(room_temperature) == original_len, "room_temperature has changed len unintentionally"
        assert len(room_temperature_for_lookup) == original_len + 2

        time_table = np.append(np.insert(time_seconds, 0, from_ns_to_s(start_date) - controller_comm_step),
                               from_ns_to_s(end_date) + controller_comm_step)
        in_room_temperature_table = create_lookup_table(time_table, room_temperature_for_lookup)

        model = SystemModel4Parameters(C_air,
                                       G_box,
                                       C_heater,
                                       G_heater, V_heater, I_heater,
                                       lower_bound, heating_time, heating_gap, temperature_desired,
                                       initial_box_temperature,
                                       initial_heat_temperature,
                                       room_temperature[0])

        # Wire the lookup table to the _plant
        model.plant.in_room_temperature = lambda: in_room_temperature_table(model.time())

        self._l.debug(f"controller_comm_step={controller_comm_step}")

        # Start simulation
        sol = ModelSolver().simulate(model, time_seconds[0], time_seconds[-1] + controller_comm_step,
                               controller_comm_step, controller_comm_step / 10.0,
                               t_eval=time_seconds)

        times_align = len(sol.t) == len(time_seconds)
        if not times_align:
            msg = f"The resulting simulation signals and the time range of the in_room_temperature should be aligned. " \
                  f"Instead, got {len(sol.t)} samples from simulation and {len(time_seconds)} input samples. " \
                  f"This could be caused by bad choice of controller communication step (currently at {controller_comm_step})." \
                  f"End time points of simulation are ({sol.t[0]}, {sol.t[-1]}). " \
                  f"End time points of db are ({time_seconds[0]}, {time_seconds[-1]})"
            self._l.error(msg)
            reply_fun({"error": msg})
            return

        state_names = model.state_names()
        state_over_time = sol.y

        def get_signal(state):
            index = np.where(state_names == state)
            assert len(index) == 1
            signal = state_over_time[index[0], :][0]
            return signal.tolist()

        T_solution = get_signal("plant.T")
        T_heater_solution = get_signal("plant.T_heater")

        # Interpolate model.plant.signals['in_heater_on'] model signals into same timeline as sol.t
        in_heater_on_interp = np.interp(sol.t, model.signals['time'], model.plant.signals['in_heater_on'])

        # All data is now aligned
        assert len(sol.t) == len(T_solution) == len(room_temperature) == len(T_heater_solution) == len(in_heater_on_interp)

        # Convert in_heater_on_interp to a python boolean array
        in_heater_on_interp_bool = [bool(x > 0.5) for x in in_heater_on_interp]

        # Convert results into format that is closer to the data in the database
        data_convert = {
            "time": sol.t,
            "average_temperature": T_solution,
            "room_temperature": room_temperature,
            "heater_temperature": T_heater_solution,
            "heater_on": in_heater_on_interp_bool
        }

        params = {
            "C_air": C_air,
            "G_box": G_box,
            "C_heater": C_heater,
            "G_heater": G_heater,
            "lower_bound": lower_bound,
            "heating_time": heating_time,
            "heating_gap": heating_gap,
            "temperature_desired": temperature_desired,
            "controller_comm_step": controller_comm_step
        }

        if as_lld:
            results_db = convert_to_results_db(data_convert, params,
                                               measurement="low_level_driver",
                                               tags={
                                                   "source": "low_level_driver"
                                               })
        else:
            results_db = convert_to_results_db(data_convert, params,
                                               measurement="physical_twin_simulator_4params",
                                               tags={
                                                   "source": "physical_twin_simulator_4params",
                                                   "experiment": "What-If-Experiment"
                                               })

        # Record results into db if specified
        if record:
            self.write_to_db(results_db, self.client)

        # Send results back.
        reply_fun(results_db)

    def write_to_db(self, results_db, client):
        self._l.debug(f"Writing {len(results_db)} samples to database.")
        write_api = client.write_api(write_options=SYNCHRONOUS)
        write_api.write(self._influxdb_bucket, self._influxdb_org, results_db)
        self._l.debug(f"Written {len(results_db)} samples to database.")
