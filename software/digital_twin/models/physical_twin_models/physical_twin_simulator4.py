import logging
from datetime import datetime

from oomodelling import ModelSolver

from communication.server.rpc_server import RPCServer
from communication.shared.connection_parameters import *
from communication.shared.protocol import ROUTING_KEY_PTSIMULATOR4, from_ns_to_s, from_s_to_ns
from digital_twin.data_access.dbmanager.data_access_parameters import INFLUXDB_TOKEN, INFLUXDB_ORG, INFLUXDB_BUCKET
from digital_twin.models.physical_twin_models.system_model4 import SystemModel4Parameters
from digital_twin.models.plant_models.four_parameters_model.best_parameters import four_param_model_params


class PhysicalTwinSimulator4Params(RPCServer):

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
        self._influx_url = influx_url
        self._influx_token = influx_token,
        self._influxdb_org = influxdb_org,
        self._influxdb_bucket = influxdb_bucket

    def start_serving(self):
        super(PhysicalTwinSimulator4Params, self).start_serving(ROUTING_KEY_PTSIMULATOR4, ROUTING_KEY_PTSIMULATOR4)

    def on_run_historical(self, start_date, end_date, record):
        # convert start and end dates to seconds
        start_date_s = from_ns_to_s(start_date)
        end_date_s = from_ns_to_s(end_date)

        # TODO: Access database to get the data needed.

        # TODO: Access database to get controller parameters

        # TODO: Access database to get most recent simulation parameters.

        # Start simulation
        results_model = self.run_simulation(start_date_s, end_date_s)

        # Convert results into format that is closer to the data in the database
        results_db = self.convert_results(results_model)

        # Send results back, or record them into the database.
        return results_db

    def run_simulation(self, start_date_s, end_date_s, step=3.0):
        C_air_num = four_param_model_params[0]
        G_box_num = four_param_model_params[1]
        C_heater_num = four_param_model_params[2]
        G_heater_num = four_param_model_params[3]
        model = SystemModel4Parameters(C_air=C_air_num,
                                       G_box=G_box_num,
                                       C_heater=C_heater_num,
                                       G_heater=G_heater_num)
        ModelSolver().simulate(model, start_date_s, end_date_s, step)
        return model

    def convert_results(self, results_model):
        results_db = []
        time = results_model.signals["time"]
        average_temperature = results_model.plant.signals['T']
        room_temperature = results_model.plant.signals['in_room_temperature']
        heater_temperature = results_model.plant.signals['T_heater']
        heater_on = results_model.plant.signals['in_heater_on']

        for (t, T, Tr, Th, H) in zip(time, average_temperature, room_temperature, heater_temperature, heater_on):
            point = {
                "measurement": "physical_twin_simulator_4params",
                "time": from_s_to_ns(t),
                "tags": {
                    "source": "physical_twin_simulator_4params"
                },
                "fields": {
                    "t1": Tr,
                    "average_temperature": T,
                    "heater_on": H,
                    "heater_temperature": Th
                }
            }
            results_db.append(point)

        return results_db
