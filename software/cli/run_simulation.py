import logging
import time
from datetime import datetime, timedelta

from communication.server.rpc_client import RPCClient
from communication.shared.protocol import ROUTING_KEY_PTSIMULATOR4, from_s_to_ns
from digital_twin.models.plant_models.four_parameters_model.best_parameters import four_param_model_params
from startup.logging_config import config_logging

DATE_FORMAT = "%Y-%m-%dT%H:%M:%S.%f"

if __name__ == '__main__':
    C_air = four_param_model_params[0]
    G_box = four_param_model_params[1]
    C_heater = four_param_model_params[2]
    G_heater = four_param_model_params[3]

    def get_date_ns(date_string):
        return from_s_to_ns(datetime.strptime(date_string, DATE_FORMAT).timestamp())

    end_date = datetime.now()
    start_date = end_date - timedelta(minutes=10)

    end_date_ns = from_s_to_ns(end_date.timestamp())
    print(end_date_ns)
    start_date_ns = from_s_to_ns(start_date.timestamp())

    config_logging(level=logging.WARN)
    client = RPCClient(ip="localhost")
    client.connect_to_server()

    reply = client.invoke_method(ROUTING_KEY_PTSIMULATOR4, "run_historical", {"start_date": start_date_ns,
                                                                              "end_date": end_date_ns,
                                                                              "C_air": C_air,
                                                                              "G_box": G_box,
                                                                              "C_heater": C_heater,
                                                                              "G_heater": G_heater,
                                                                              "lower_bound": 5.0,
                                                                              "heating_time": 20.0,
                                                                              "heating_gap": 30.0,
                                                                              "temperature_desired": 35.0,
                                                                              "controller_comm_step": 3.0,
                                                                              "initial_box_temperature": 21.0,
                                                                              "initial_heat_temperature": 21.0,
                                                                              "record": True})
    print(reply)
