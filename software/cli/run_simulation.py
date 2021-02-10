import logging
from datetime import datetime

import pytz

from digital_twin.communication.rabbitmq_protocol import ROUTING_KEY_PTSIMULATOR4
from incubator.communication.server.rpc_client import RPCClient
from incubator.communication.shared.protocol import from_s_to_ns
from incubator.models.plant_models.four_parameters_model.best_parameters import four_param_model_params
from startup.utils.logging_config import config_logging

if __name__ == '__main__':
    C_air = four_param_model_params[0]
    G_box = four_param_model_params[1]
    C_heater = four_param_model_params[2]
    G_heater = four_param_model_params[3]

    start_date = datetime.fromisoformat("2021-01-04 09:56:36").astimezone(pytz.utc)
    end_date = datetime.fromisoformat("2021-01-04 10:11:36").astimezone(pytz.utc)

    end_date_ns = from_s_to_ns(end_date.timestamp())
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
                                                                              "temperature_desired": 25.0,
                                                                              "controller_comm_step": 3.0,
                                                                              "initial_box_temperature": 21.0,
                                                                              "initial_heat_temperature": 21.0,
                                                                              "record": True})
    print(reply)
