import logging
from datetime import datetime, timedelta

from communication.server.rpc_client import RPCClient
from communication.shared.protocol import ROUTING_KEY_PLANTSIMULATOR4, from_s_to_ns
from digital_twin.data_access.dbmanager.incubator_data_query import IncubatorDataQuery
from digital_twin.models.plant_models.four_parameters_model.best_parameters import four_param_model_params
from startup.logging_config import config_logging

if __name__ == '__main__':
    config_logging(level=logging.DEBUG)
    C_air = four_param_model_params[0]
    G_box = four_param_model_params[1]
    C_heater = four_param_model_params[2]
    G_heater = four_param_model_params[3]

    end_date = datetime.now()
    start_date = end_date - timedelta(minutes=2)

    end_date_ns = from_s_to_ns(end_date.timestamp())
    start_date_ns = from_s_to_ns(start_date.timestamp())

    with IncubatorDataQuery() as db:
        room_temp_data = db.query(start_date_ns, end_date_ns, "low_level_driver", "t1")
        average_temperature_data = db.query(start_date_ns, end_date_ns, "low_level_driver", "average_temperature")
        # heater_data = db.query(start_date, end_date, "low_level_driver", "heater_on")

    time_seconds = room_temp_data.apply(lambda row: row["_time"].timestamp(), axis=1).to_numpy().tolist()
    room_temperature = room_temp_data["_value"].to_numpy().tolist()
    average_temperature = average_temperature_data["_value"].to_numpy().tolist()
    # heater_on = heater_data["_value"].to_numpy()
    heater_on = [False for t in time_seconds]

    client = RPCClient(ip="localhost")
    client.connect_to_server()

    reply = client.invoke_method(ROUTING_KEY_PLANTSIMULATOR4, "run", {"timespan_seconds": time_seconds,
                                                                      "C_air": C_air,
                                                                      "G_box": G_box,
                                                                      "C_heater": C_heater,
                                                                      "G_heater": G_heater,
                                                                      "initial_box_temperature": average_temperature[0],
                                                                      "initial_heat_temperature": 21.0,
                                                                      "room_temperature": room_temperature,
                                                                      "heater_on": heater_on})
    print(reply)
