import logging

import numpy as np
from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS
from oomodelling import ModelSolver

from communication.server.rpc_server import RPCServer
from communication.shared.connection_parameters import *
from communication.shared.protocol import ROUTING_KEY_PTSIMULATOR4, from_ns_to_s, from_s_to_ns
from digital_twin.data_access.dbmanager.data_access_parameters import INFLUXDB_TOKEN, INFLUXDB_ORG, INFLUXDB_BUCKET, \
    INFLUXDB_URL
from digital_twin.data_access.dbmanager.incubator_data_conversion import convert_to_results_db
from digital_twin.data_access.dbmanager.incubator_data_query import query
from digital_twin.models.physical_twin_models.system_model4 import SystemModel4Parameters
from digital_twin.models.plant_models.model_functions import create_lookup_table


class PhysicalTwinSimulator4Params(RPCServer):
    """
    Can run simulations of the physical twin. This includes controller and plant.
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
        self._l = logging.getLogger("PhysicalTwinSimulator4Params")
        self.client = InfluxDBClient(url=influx_url, token=influx_token, org=INFLUXDB_ORG)
        self._influxdb_bucket = influxdb_bucket
        self._influxdb_org = influxdb_org

    def start_serving(self):
        super(PhysicalTwinSimulator4Params, self).start_serving(ROUTING_KEY_PTSIMULATOR4, ROUTING_KEY_PTSIMULATOR4)

    def on_run_historical(self, start_date, end_date,
                          C_air,
                          G_box,
                          C_heater,
                          G_heater,
                          lower_bound, heating_time, heating_gap, temperature_desired,
                          controller_comm_step,
                          initial_box_temperature,
                          initial_heat_temperature,
                          record):
        # Access database to get the data needed.
        query_api = self.client.query_api()
        room_temp_results = query(query_api, self._influxdb_bucket, start_date, end_date, "low_level_driver", "t1")

        # Check if there are results
        if room_temp_results.empty:
            error_msg = f"No room temperature data exists in the period specified " \
                        f"by start_date={start_date} and end_date={end_date}."
            self._l.warning(error_msg)
            return {"error": error_msg}

        # convert start and end dates to seconds
        # This is needed because the simulation runs in seconds.
        start_date_s = from_ns_to_s(start_date)
        end_date_s = from_ns_to_s(end_date)

        # Convert results into format that simulation model can take
        time_seconds = room_temp_results.apply(lambda row: row["_time"].timestamp(), axis=1).to_numpy()
        room_temperature = room_temp_results["_value"].to_numpy()

        # The following is true because of the query we made at the db
        assert time_seconds[0] >= start_date_s

        # Ensure that the start_date is in the lookup table.
        # We need to do this because the data in the database may not exist at exactly the start date.
        # So we need to interpolate it from the data that exists.
        time_seconds = np.insert(time_seconds, 0, start_date_s)
        room_temperature = np.insert(room_temperature, 0, room_temperature[0])
        in_room_temperature_table = create_lookup_table(time_seconds, room_temperature)

        model = SystemModel4Parameters(C_air,
                                       G_box,
                                       C_heater,
                                       G_heater,
                                       lower_bound, heating_time, heating_gap, temperature_desired,
                                       initial_box_temperature,
                                       initial_heat_temperature)

        # Wire the lookup table to the model
        model.plant.in_room_temperature = lambda: in_room_temperature_table(model.time())

        # Start simulation
        ModelSolver().simulate(model, start_date_s, end_date_s, controller_comm_step)

        # Convert results into format that is closer to the data in the database
        data_convert = {
            "time": model.signals["time"],
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
        return results_db

    def write_to_db(self, results_db, client):
        self._l.debug(f"Writing {len(results_db)} samples to database.")
        write_api = client.write_api(write_options=SYNCHRONOUS)
        write_api.write(self._influxdb_bucket, self._influxdb_org, results_db)
        self._l.debug(f"Written {len(results_db)} samples to database.")
