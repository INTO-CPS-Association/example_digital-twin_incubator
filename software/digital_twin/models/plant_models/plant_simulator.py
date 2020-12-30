import logging

from influxdb_client.client.write_api import SYNCHRONOUS
from oomodelling import ModelSolver

from communication.server.rpc_server import RPCServer
from communication.shared.connection_parameters import *
from communication.shared.protocol import from_s_to_ns, \
    ROUTING_KEY_PLANTSIMULATOR4
from digital_twin.data_access.dbmanager.data_access_parameters import INFLUXDB_TOKEN, INFLUXDB_ORG, INFLUXDB_BUCKET
from digital_twin.data_access.dbmanager.incubator_data_query import IncubatorDataQuery
from digital_twin.models.plant_models.four_parameters_model.four_parameter_model import FourParameterIncubatorPlant
from digital_twin.models.plant_models.model_functions import create_lookup_table
import numpy as np


class PlantSimulator4Params(RPCServer):
    """
    Can run simulations of the plant.
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
        self._l = logging.getLogger("PhysicalTwinSimulator4Params")
        self.db = IncubatorDataQuery(url=influx_url, token=influx_token, org=influxdb_org, bucket=influxdb_bucket)

    def start_serving(self):
        super(PlantSimulator4Params, self).start_serving(ROUTING_KEY_PLANTSIMULATOR4, ROUTING_KEY_PLANTSIMULATOR4)

    def on_run_historical(self, start_date, end_date,
                          C_air,
                          G_box,
                          C_heater,
                          G_heater,
                          initial_heat_temperature):
        self._l.debug("Accessing database to get the data needed.")
        # This might look ineficient, but querying for all fields at the same time makes the a list of dataframes
        # And that list does not follow the same order of the fields asked.
        # So this solution is less efficient, but more predictable.
        room_temp_data = self.db.query(start_date, end_date, "low_level_driver", "t1")
        heater_data = self.db.query(start_date, end_date, "low_level_driver", "heater_on")
        average_temperature_data = self.db.query(start_date, end_date, "low_level_driver", "average_temperature")

        self._l.debug("Ensuring that we have a consistent set of samples.")
        if not (len(room_temp_data) == len(heater_data) == len(average_temperature_data)):
            error_msg = f"Inconsistent number of samples found for " \
                        f"start_date={start_date} and end_date={end_date}." \
                        f"len(room_temp_data)={len(room_temp_data)}" \
                        f"len(heater_data)={len(heater_data)}" \
                        f"len(average_temperature)={len(average_temperature_data)}"
            self._l.warning(error_msg)
            return {"error": error_msg}

        self._l.debug("Checking if there are enough samples.")
        if len(room_temp_data) < 1:
            error_msg = f"Not enough physical twin data exists in the period specified " \
                        f"by start_date={start_date} and end_date={end_date}. Found only {len(room_temp_data)} samples."
            self._l.warning(error_msg)
            return {"error": error_msg}

        self._l.debug("Converting results to numpy and time to seconds.")
        time_seconds = room_temp_data.apply(lambda row: row["_time"].timestamp(), axis=1).to_numpy()
        room_temperature = room_temp_data["_value"].to_numpy()
        average_temperature = average_temperature_data["_value"].to_numpy()

        room_temperature_fun = create_lookup_table(time_seconds, room_temperature)
        heater_on_fun = create_lookup_table(time_seconds, heater_data["_value"].to_numpy())

        self._l.debug("Wiring model.")
        model = FourParameterIncubatorPlant(initial_room_temperature=room_temperature[0],
                                            initial_box_temperature=average_temperature[0],
                                            initial_heat_temperature=initial_heat_temperature,
                                            C_air=C_air, G_box=G_box,
                                            C_heater=C_heater, G_heater=G_heater)
        model.in_room_temperature = lambda: room_temperature_fun(model.time())
        model.in_heater_on = lambda: heater_on_fun(model.time())

        start_t = time_seconds[0]
        end_t = time_seconds[-1]
        max_step_size = time_seconds[1]-time_seconds[0]

        self._l.debug(f"Simulating model from time {start_t} to {end_t} with a maximum step size of {max_step_size}, "
                      f"and a total of {len(time_seconds)} samples.")
        sol = ModelSolver().simulate(model, start_t, end_t, max_step_size,
                               t_eval=time_seconds)

        self._l.debug(f"Converting solution to influxdb data format.")
        state_names = model.state_names()
        state_over_time = sol.y
        self._l.debug(f"Solution has {len(state_over_time[0])} samples.")

        def get_signal(state):
            index = np.where(state_names == state)
            assert len(index) == 1
            signal = state_over_time[index[0], :][0]
            return signal

        T_solution = get_signal("T")
        T_heater_solution = get_signal("T_heater")

        results = self.convert_results(time_seconds, T_solution, T_heater_solution,
                                       C_air, G_box, C_heater, G_heater)

        self._l.debug(f"Sending results back.")
        return results

    def convert_results(self, time_seconds, T_solution, T_heater_solution,
                                       C_air, G_box, C_heater, G_heater):
        results_db = []

        # Record a single point with all the parameters
        point = {
            "measurement": "plant_simulator_4params",
            "time": from_s_to_ns(time_seconds[0]),
            "tags": {
                "source": "parameters"
            },
            "fields": {
                "C_air": C_air,
                "G_box": G_box,
                "C_heater": C_heater,
                "G_heater": G_heater
            }
        }
        results_db.append(point)

        for (t, T, Th) in zip(time_seconds, T_solution, T_heater_solution):
            point = {
                "measurement": "physical_twin_simulator_4params",
                "time": from_s_to_ns(t),
                "tags": {
                    "source": "simulation"
                },
                "fields": {
                    "average_temperature": T,
                    "heater_temperature": Th
                }
            }
            results_db.append(point)

        return results_db
