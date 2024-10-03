import logging
from datetime import datetime

import pytz
from influxdb_client import InfluxDBClient

from digital_twin.communication.rabbitmq_protocol import ROUTING_KEY_PLANTSIMULATOR4
from digital_twin.data_access.dbmanager.data_access_parameters import INFLUXDB_URL, INFLUXDB_TOKEN, INFLUXDB_BUCKET, \
    INFLUXDB_ORG
from digital_twin.data_access.dbmanager.incubator_data_query import query
from incubator.communication.server.rpc_client import RPCClient
from incubator.communication.shared.protocol import from_s_to_ns
from incubator.config.config import load_config
from incubator.models.plant_models.four_parameters_model.best_parameters import four_param_model_params
from incubator.visualization.data_plotting import plotly_incubator_data, show_plotly
from startup.utils.logging_config import config_logging


def run_plant_simulation(params, start_date, end_date, initial_heat_temperature, record):
    C_air = params[0]
    G_box = params[1]
    C_heater = params[2]
    G_heater = params[3]

    end_date_ns = from_s_to_ns(end_date.timestamp())
    start_date_ns = from_s_to_ns(start_date.timestamp())

    db = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
    query_api = db.query_api()
    room_temp_data = query(query_api, INFLUXDB_BUCKET, start_date_ns, end_date_ns, "low_level_driver", "t3")
    average_temperature_data = query(query_api, INFLUXDB_BUCKET, start_date_ns, end_date_ns, "low_level_driver",
                                     "average_temperature")
    heater_data = query(query_api, INFLUXDB_BUCKET, start_date_ns, end_date_ns, "low_level_driver", "heater_on")
    fan_data = query(query_api, INFLUXDB_BUCKET, start_date_ns, end_date_ns, "low_level_driver", "fan_on")

    time_seconds = room_temp_data.apply(lambda row: row["_time"].timestamp(), axis=1).to_numpy().tolist()
    room_temperature = room_temp_data["t3"].to_numpy().tolist()
    average_temperature = average_temperature_data["average_temperature"].to_numpy().tolist()
    heater_on = heater_data["heater_on"].to_numpy().tolist()
    fan_on = fan_data["fan_on"].to_numpy().tolist()

    config = load_config("startup.conf")
    client = RPCClient(**(config["rabbitmq"]))
    client.connect_to_server()

    sim = client.invoke_method(ROUTING_KEY_PLANTSIMULATOR4, "run", {
        "tags": {
            "experiment": "cli_run_plant_simulation",
        },
        "timespan_seconds": time_seconds,
        "C_air": C_air,
        "G_box": G_box,
        "C_heater": C_heater,
        "G_heater": G_heater,
        "initial_box_temperature": average_temperature[0],
        "initial_heat_temperature": initial_heat_temperature,
        "room_temperature": room_temperature,
        "heater_on": heater_on,
        "record": record
    })

    data = {"time": time_seconds,
            "heater_on": heater_on,
            "fan_on": fan_on,
            "average_temperature": average_temperature,
            "t3": room_temperature}

    fig = plotly_incubator_data(data, compare_to={
        "T(4)": {
            "time": time_seconds,
            "T": sim["average_temperature"],
        }
    }, heater_T_data={
        "T(4)": {
            "time": time_seconds,
            "T_heater": sim["heater_temperature"],
        }
    }, show_actuators=True)
    show_plotly(fig)


if __name__ == '__main__':
    config_logging(level=logging.DEBUG)

    start_date = datetime.fromisoformat("2021-01-04 09:56:36").astimezone(pytz.utc)
    end_date = datetime.fromisoformat("2021-01-04 10:11:36").astimezone(pytz.utc)

    params = four_param_model_params
    run_plant_simulation(params, start_date, end_date, initial_heat_temperature=21.0, record=False)
