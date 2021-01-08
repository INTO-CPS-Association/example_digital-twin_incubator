import logging

from digital_twin.models.plant_models.four_parameters_model.best_parameters import four_param_model_params
from digital_twin.monitoring.kalman_filter_plant_server import KalmanFilterPlantServer
from startup.logging_config import config_logging

if __name__ == '__main__':
    config_logging(filename="kalman_filter.log", level=logging.DEBUG)
    monitor = KalmanFilterPlantServer(ip="localhost")

    C_air = four_param_model_params[0]
    G_box = four_param_model_params[1]
    C_heater = four_param_model_params[2]
    G_heater = four_param_model_params[3]

    monitor.start_monitoring(step_size=3.0, std_dev=0.1,
                             C_air=C_air, G_box=G_box, C_heater=C_heater, G_heater=G_heater,
                             initial_heater_temperature=25.0, initial_box_temperature=25.0)
