import logging
from datetime import datetime

from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS
from oomodelling import ModelSolver

from communication.server.rpc_server import RPCServer
from communication.shared.connection_parameters import *
from communication.shared.protocol import ROUTING_KEY_PTSIMULATOR4, from_ns_to_s, from_s_to_ns
from digital_twin.data_access.dbmanager.data_access_parameters import INFLUXDB_TOKEN, INFLUXDB_ORG, INFLUXDB_BUCKET
from digital_twin.models.physical_twin_models.system_model4 import SystemModel4Parameters


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
        self._influx_token = influx_token
        self._influxdb_org = influxdb_org
        self._influxdb_bucket = influxdb_bucket

    def start_serving(self):
        super(PhysicalTwinSimulator4Params, self).start_serving(ROUTING_KEY_PTSIMULATOR4, ROUTING_KEY_PTSIMULATOR4)

    def on_run_historical(self, start_date, end_date,
                          C_air,
                          G_box,
                          C_heater,
                          G_heater,
                          lower_bound, heating_time, heating_gap, desired_temperature,
                          controller_comm_step,
                          initial_box_temperature,
                          initial_heat_temperature,
                          record):
        # convert start and end dates to seconds
        start_date_s = from_ns_to_s(start_date)
        end_date_s = from_ns_to_s(end_date)

        # TODO: Access database to get the data needed.

        # Start simulation
        model = SystemModel4Parameters(C_air,
                                       G_box,
                                       C_heater,
                                       G_heater,
                                       lower_bound, heating_time, heating_gap, desired_temperature,
                                       initial_box_temperature,
                                       initial_heat_temperature)
        ModelSolver().simulate(model, start_date_s, end_date_s, controller_comm_step)

        # Convert results into format that is closer to the data in the database
        results_db = self.convert_results(model,
                                          C_air,
                                          G_box,
                                          C_heater,
                                          G_heater,
                                          lower_bound, heating_time, heating_gap, desired_temperature,
                                          controller_comm_step)

        # Record results into db if specified
        if record:
            self.write_to_db(results_db)

        # Send results back.
        return results_db

    def convert_results(self, results_model,
                        C_air,
                        G_box,
                        C_heater,
                        G_heater,
                        lower_bound, heating_time, heating_gap, desired_temperature,
                        controller_comm_step):
        results_db = []
        time = results_model.signals["time"]
        average_temperature = results_model.plant.signals['T']
        room_temperature = results_model.plant.signals['in_room_temperature']
        heater_temperature = results_model.plant.signals['T_heater']
        heater_on = results_model.plant.signals['in_heater_on']

        # Record a single point with all the parameters
        point = {
            "measurement": "physical_twin_simulator_4params",
            "time": from_s_to_ns(time[0]),
            "tags": {
                "source": "parameters"
            },
            "fields": {
                "C_air": C_air,
                "G_box": G_box,
                "C_heater": C_heater,
                "G_heater": G_heater,
                "lower_bound": lower_bound,
                "heating_time": heating_time,
                "heating_gap": heating_gap,
                "desired_temperature": desired_temperature,
                "controller_comm_step": controller_comm_step
            }
        }
        results_db.append(point)

        for (t, T, Tr, Th, H) in zip(time, average_temperature, room_temperature, heater_temperature, heater_on):
            point = {
                "measurement": "physical_twin_simulator_4params",
                "time": from_s_to_ns(t),
                "tags": {
                    "source": "simulation"
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

    def write_to_db(self, results_db):
        self._l.debug(f"Writting {len(results_db)} samples to database.")
        self._l.debug(f"Database information: url={self._influx_url}; token={self._influx_token}.")
        client = InfluxDBClient(url=self._influx_url, token=self._influx_token)
        write_api = client.write_api(write_options=SYNCHRONOUS)
        write_api.write(self._influxdb_bucket, self._influxdb_org, results_db)
        self._l.debug(f"Written {len(results_db)} samples to database.")
