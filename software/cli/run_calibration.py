import logging
from datetime import datetime, timedelta

import pytz

from cli.run_plant_simulation import run_plant_simulation
from communication.server.rpc_client import RPCClient
from communication.shared.protocol import ROUTING_KEY_PLANTSIMULATOR4, from_s_to_ns, ROUTING_KEY_PLANTCALIBRATOR4
from digital_twin.models.plant_models.four_parameters_model.best_parameters import four_param_model_params
from startup.logging_config import config_logging

if __name__ == '__main__':
    C_air = four_param_model_params[0]
    G_box = four_param_model_params[1]
    C_heater = four_param_model_params[2]
    G_heater = four_param_model_params[3]

    start_date = datetime.fromisoformat("2020-12-31 09:40:00").astimezone(pytz.utc)
    end_date = datetime.fromisoformat("2020-12-31 09:50:00").astimezone(pytz.utc)
    # end_date = datetime.now()
    # start_date = end_date - timedelta(minutes=10)
    print(f"start_date={start_date}")
    print(f"end_date={end_date}")

    end_date_ns = from_s_to_ns(end_date.timestamp())
    start_date_ns = from_s_to_ns(start_date.timestamp())

    config_logging(level=logging.WARN)
    client = RPCClient(ip="localhost")
    client.connect_to_server()

    reply = client.invoke_method(ROUTING_KEY_PLANTCALIBRATOR4, "run_calibration", {"start_date_ns": start_date_ns,
                                                                                   "end_date_ns": end_date_ns,
                                                                                   "Nevals": 100})
    params = [reply["C_air"],
                          reply["G_box"],
                          reply["C_heater"],
                          reply["G_heater"],
                          reply["initial_heat_temperature"]]
    print(params)
    run_plant_simulation(params, start_date, end_date)
