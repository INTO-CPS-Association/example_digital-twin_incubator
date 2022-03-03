import logging

import numpy as np
from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS
from oomodelling import ModelSolver

from digital_twin.communication.rabbitmq_protocol import ROUTING_KEY_PTSIMULATOR4
from digital_twin.data_access.dbmanager.incubator_data_conversion import convert_to_results_db
from digital_twin.data_access.dbmanager.incubator_data_query import query, query_convert_aligned_data
from incubator.communication.server.rpc_server import RPCServer
from incubator.communication.shared.protocol import from_ns_to_s
from incubator.models.physical_twin_models.system_model4 import SystemModel4Parameters
from incubator.models.plant_models.model_functions import create_lookup_table


class PhysicalTwinSimulator4Params(RPCServer):
    """
    Can run simulations of the physical twin. This includes controller and plant.
    """

    def __init__(self, rabbitmq_config, influxdb_config):
        super().__init__(**rabbitmq_config)
        self._l = logging.getLogger("PhysicalTwinSimulator4Params")
        self.client = InfluxDBClient(**influxdb_config)
        self._influxdb_bucket = influxdb_config["bucket"]
        self._influxdb_org = influxdb_config["org"]

    def setup(self):
        super(PhysicalTwinSimulator4Params, self).setup(ROUTING_KEY_PTSIMULATOR4, ROUTING_KEY_PTSIMULATOR4)

    def run_historical(self, start_date, end_date,
                       C_air,
                       G_box,
                       C_heater,
                       G_heater,
                       lower_bound, heating_time, heating_gap, temperature_desired,
                       controller_comm_step,
                       initial_box_temperature,
                       initial_heat_temperature,
                       record,
                       as_lld,
                       reply_fun):
        # Access database to get the data needed.
        query_api = self.client.query_api()

        time_seconds, results = query_convert_aligned_data(query_api, self._influxdb_bucket, start_date, end_date, {
            "low_level_driver": ["t1"]
        })

        # Ensure that the start_date and end_date are in the lookup table.
        # We need to do this because the data in the database may not exist at exactly these dates.
        # So we need to interpolate it from the data that exists.
        room_temperature = results["low_level_driver"]["t1"]
        room_temperature = np.append(np.insert(room_temperature, 0, room_temperature[0]), room_temperature[-1])

        time_table = np.append(np.insert(time_seconds, 0, from_ns_to_s(start_date)-controller_comm_step), from_ns_to_s(end_date)+controller_comm_step)
        in_room_temperature_table = create_lookup_table(time_table, room_temperature)

        model = SystemModel4Parameters(C_air,
                                       G_box,
                                       C_heater,
                                       G_heater,
                                       lower_bound, heating_time, heating_gap, temperature_desired,
                                       initial_box_temperature,
                                       initial_heat_temperature)

        # Wire the lookup table to the _model
        model.plant.in_room_temperature = lambda: in_room_temperature_table(model.time())

        self._l.debug(f"controller_comm_step={controller_comm_step}")

        # Start simulation
        sol = ModelSolver().simulate(model, time_seconds[0], time_seconds[-1]+controller_comm_step, controller_comm_step)

        times_align = len(model.signals["time"]) == len(time_seconds)
        if not times_align:
            msg = f"The resulting simulation signals and the time range of the in_room_temperature should be aligned. " \
                  f"Instead, got {len(model.signals['time'])} samples from simulation and {len(time_seconds)} input samples. " \
                  f"This could be caused by bad choice of controller communication step (currently at {controller_comm_step})." \
                  f"End time points of simulation are ({model.signals['time'][0]}, {model.signals['time'][-1]}). " \
                    f"End time points of db are ({time_seconds[0]}, {time_seconds[-1]})"
            self._l.error(msg)
            reply_fun({"error": msg})
            return

        # Convert results into format that is closer to the data in the database
        data_convert = {
            "time": time_seconds,
            "average_temperature": model.plant.signals['T'],
            "room_temperature": model.plant.signals['in_room_temperature'],
            "heater_temperature": model.plant.signals['T_heater'],
            "heater_on": model.plant.signals['in_heater_on']
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
