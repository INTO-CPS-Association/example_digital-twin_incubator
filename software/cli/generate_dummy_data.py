from datetime import datetime, timedelta

from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS

import numpy as np

from digital_twin.communication.rabbitmq_protocol import ROUTING_KEY_PTSIMULATOR4
from incubator.communication.server.rpc_client import RPCClient
from incubator.communication.shared.protocol import from_s_to_ns
from incubator.config.config import config_logger, load_config
from incubator.models.plant_models.room_temperature_model import room_temperature


def generate_room_data(influxdb_config, start_date, end_date):
    start_date_s = start_date.timestamp()
    end_date_s = end_date.timestamp()

    client = InfluxDBClient(**influxdb_config)
    bucket = influxdb_config["bucket"]
    org = influxdb_config["org"]

    # Get write-api
    write_api = client.write_api(write_options=SYNCHRONOUS)

    # Construct points
    timerange_s = np.arange(start_date_s, end_date_s, 3.0)

    def point(t):
        t_ns = from_s_to_ns(t)
        return {
            "measurement": "low_level_driver",
            "time": t_ns,
            "tags": {
                "source": "low_level_driver"
            },
            "fields": {
                "t1": room_temperature(t),
                "time_t1": t_ns,
            }
        }

    points = [point(t) for t in timerange_s]

    # Write them to DB
    write_api.write(bucket, org, points)


def generate_incubator_exec_data(config, start_date, end_date):
    start_date_ns = from_s_to_ns(start_date.timestamp())
    end_date_ns = from_s_to_ns(end_date.timestamp())

    client = RPCClient(**(config["rabbitmq"]))
    client.connect_to_server()

    params = {"start_date": start_date_ns,
              "end_date": end_date_ns,
              "controller_comm_step": 3.0,
              "record": True,
              "as_lld": True}

    params_plant = config["digital_twin"]["models"]["plant"]["param4"]
    for k in params_plant:
        params[k] = params_plant[k]

    params_ctrl = config["physical_twin"]["controller"]
    for k in params_ctrl:
        params[k] = params_ctrl[k]

    reply = client.invoke_method(ROUTING_KEY_PTSIMULATOR4, "run_historical", params)
    if "error" in reply:
        print(reply)


def generate_dummy_data():
    config_logger("logging.conf")
    config = load_config("startup.conf")

    # Time range for the fake data
    end_date = datetime.now()
    start_date = end_date - timedelta(hours=10)

    generate_room_data(config["influxdb"], start_date, end_date)

    generate_incubator_exec_data(config, start_date, end_date)


if __name__ == '__main__':
    generate_dummy_data()
