import logging
from datetime import datetime, timedelta

import dateutil
import pytz

from communication.server.rpc_client import RPCClient
from communication.shared.protocol import ROUTING_KEY_PLANTSIMULATOR4, from_s_to_ns
from digital_twin.data_access.dbmanager.incubator_data_query import IncubatorDataQuery
from digital_twin.models.plant_models.four_parameters_model.best_parameters import four_param_model_params
from digital_twin.visualization.data_plotting import plotly_incubator_data, show_plotly
from startup.logging_config import config_logging

def run_plant_simulation(params, start_date, end_date):
    C_air = params[0]
    G_box = params[1]
    C_heater = params[2]
    G_heater = params[3]
    initial_heat_temperature = params[4]

    end_date_ns = from_s_to_ns(end_date.timestamp())
    start_date_ns = from_s_to_ns(start_date.timestamp())

    with IncubatorDataQuery() as db:
        room_temp_data = db.query(start_date_ns, end_date_ns, "low_level_driver", "t1")
        average_temperature_data = db.query(start_date_ns, end_date_ns, "low_level_driver", "average_temperature")
        heater_data = db.query(start_date_ns, end_date_ns, "low_level_driver", "heater_on")
        fan_data = db.query(start_date_ns, end_date_ns, "low_level_driver", "fan_on")

    time_seconds = room_temp_data.apply(lambda row: row["_time"].timestamp(), axis=1).to_numpy().tolist()
    room_temperature = room_temp_data["_value"].to_numpy().tolist()
    average_temperature = average_temperature_data["_value"].to_numpy().tolist()
    heater_on = heater_data["_value"].to_numpy().tolist()
    fan_on = fan_data["_value"].to_numpy().tolist()

    client = RPCClient(ip="localhost")
    client.connect_to_server()

    sim = client.invoke_method(ROUTING_KEY_PLANTSIMULATOR4, "run", {"timespan_seconds": time_seconds,
                                                                    "C_air": C_air,
                                                                    "G_box": G_box,
                                                                    "C_heater": C_heater,
                                                                    "G_heater": G_heater,
                                                                    "initial_box_temperature": average_temperature[0],
                                                                    "initial_heat_temperature": initial_heat_temperature,
                                                                    "room_temperature": room_temperature,
                                                                    "heater_on": heater_on})

    data = {"time": time_seconds,
            "heater_on": heater_on,
            "fan_on": fan_on,
            "average_temperature": average_temperature,
            "t1": room_temperature}

    fig = plotly_incubator_data(data,
                                compare_to={
                                    "T(4)": {
                                        "time": time_seconds,
                                        "T": sim["T"],
                                    }
                                },
                                heater_T_data = {
                                    "T(4)": {
                                        "time": time_seconds,
                                        "T_heater": sim["T_heater"],
                                    }
                                },
                                show_actuators=True
                                )
    show_plotly(fig)


if __name__ == '__main__':
    config_logging(level=logging.DEBUG)

    start_date = datetime.fromisoformat("2020-12-31 09:40:00").astimezone(pytz.utc)
    end_date = datetime.fromisoformat("2020-12-31 09:50:00").astimezone(pytz.utc)

    params = [145.69782402, 0.79154106, 227.76228512,   1.92343277,  45.0]
    run_plant_simulation(params, start_date, end_date)
