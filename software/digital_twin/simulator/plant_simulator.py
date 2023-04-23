import logging

import numpy as np
from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS

from digital_twin.communication.rabbitmq_protocol import ROUTING_KEY_PLANTSIMULATOR4
from digital_twin.data_access.dbmanager.incubator_data_conversion import convert_to_results_db
from incubator.communication.server.rpc_server import RPCServer
from incubator.simulators.PlantSimulator4Params import PlantSimulator4Params


class PlantSimulator4ParamsServer(RPCServer):
    """
    Can run simulations of the plant.
    """

    def __init__(self, rabbitmq_config, influxdb_config):
        super().__init__(**rabbitmq_config)
        self._l = logging.getLogger("PlantSimulator4ParamsServer")
        self.client = InfluxDBClient(**influxdb_config)
        self._influxdb_bucket = influxdb_config["bucket"]
        self._influxdb_org = influxdb_config["org"]
        self.simulator = PlantSimulator4Params()

    def setup(self):
        super(PlantSimulator4ParamsServer, self).setup(ROUTING_KEY_PLANTSIMULATOR4, ROUTING_KEY_PLANTSIMULATOR4)

    def run(self, tags,
            timespan_seconds,
            C_air,
            G_box,
            C_heater,
            G_heater,
            initial_box_temperature,
            initial_heat_temperature,
            room_temperature,
            heater_on,
            record,
            reply_fun):

        self._l.debug("Ensuring that we have a consistent set of samples.")
        if not (len(room_temperature) == len(heater_on) == len(timespan_seconds)):
            error_msg = f"Inconsistent number of samples found:" \
                        f"len(room_temperature)={len(room_temperature)}" \
                        f"len(heater_on)={len(heater_on)}" \
                        f"len(timespan_seconds)={len(timespan_seconds)}"
            self._l.warning(error_msg)
            return {"error": error_msg}

        self._l.debug("Checking if there are enough samples.")
        if len(timespan_seconds) < 1:
            error_msg = f"Not enough data exists in the period specified by timespan_seconds" \
                        f"Found only {len(timespan_seconds)} samples."
            self._l.warning(error_msg)
            return {"error": error_msg}

        try:
            sol, model = self.simulator.run_simulation(timespan_seconds, initial_box_temperature, initial_heat_temperature,
                                                       room_temperature, heater_on,
                                                       C_air, G_box, C_heater, G_heater)

            self._l.debug(f"Converting solution to influxdb data format.")
            state_names = model.state_names()
            state_over_time = sol.y
            self._l.debug(f"Solution has {len(state_over_time[0])} samples.")

            def get_signal(state):
                index = np.where(state_names == state)
                assert len(index) == 1
                signal = state_over_time[index[0], :][0]
                return signal.tolist()

            T_solution = get_signal("T")
            T_heater_solution = get_signal("T_heater")

            # Maybe there's no need to send everything back.
            #  One could have a parameter that tells this component which data to send back via rabbitmq.
            #  At the same, this complicates the interface and I'm not certain this is a performance bottleneck.
            results = {
                "time": timespan_seconds,
                "average_temperature": T_solution,
                "room_temperature": room_temperature,
                "heater_temperature": T_heater_solution,
                "heater_on": heater_on
            }

            params = {
                "C_air": C_air,
                "G_box": G_box,
                "C_heater": C_heater,
                "G_heater": G_heater
            }

            if record:
                tags["source"] = "plant_simulator_4params"
                results_db = convert_to_results_db(results, params,
                                                   measurement="plant_simulator_4params",
                                                   tags=tags)
                self._l.debug(f"Writing {len(results_db)} samples to database.")
                write_api = self.client.write_api(write_options=SYNCHRONOUS)
                write_api.write(self._influxdb_bucket, self._influxdb_org, results_db)
                self._l.debug(f"Written {len(results_db)} samples to database.")

            self._l.debug(f"Sending results back.")

        except ValueError as error:
            msg = f"Exception while running simulation: {error}."
            self._l.error(msg)
            results = {"error": msg}

        reply_fun(results)
