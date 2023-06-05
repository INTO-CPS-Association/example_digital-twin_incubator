from oomodelling import Model

from incubator.monitoring.kalman_filter_4p import KalmanFilter4P
from incubator.monitoring.noise_model import NoiseFeedthrough
from incubator.models.controller_models.controller_model4 import ControllerModel4
from incubator.models.plant_models.four_parameters_model.four_parameter_model import FourParameterIncubatorPlant


class KalmanSystemModel(Model):
    def __init__(self, step_size,
                 std_dev, Theater_covariance_init, T_covariance_init,
                 C_air,
                 G_box,
                 C_heater,
                 G_heater, V_heater, I_heater,
                 initial_room_temperature, initial_box_temperature, initial_heat_temperature):
        super().__init__()

        self.ctrl = ControllerModel4(temperature_desired=35, heating_time=0.1, heating_gap=1.0)
        self.plant = FourParameterIncubatorPlant(V_heater, I_heater,
                                                 initial_room_temperature, initial_box_temperature,
                                                 initial_heat_temperature,
                                                 C_air, G_box,
                                                 C_heater, G_heater)
        self.noise_sensor = NoiseFeedthrough(std_dev)
        self.kalman = KalmanFilter4P(step_size, std_dev, Theater_covariance_init, T_covariance_init,
                                     C_air,
                                     G_box,
                                     C_heater,
                                     G_heater,
                                     V_heater, I_heater)

        # self.std_dev = self.var(lambda: 0.1 if self.time()<100 else (1.2 if self.time()<150 else 0.1))
        self.std_dev = self.var(lambda: std_dev)
        self.G_box = self.var(lambda: G_box if self.time() < 300 else (G_box * 10 if self.time() < 500 else G_box))
        # self.G_box = self.var(lambda: G_box)

        self.noise_sensor.std_dev = self.std_dev
        self.noise_sensor.u = self.plant.T
        self.ctrl.in_temperature = self.noise_sensor.y
        self.plant.in_heater_on = self.ctrl.heater_on
        self.plant.G_box = self.G_box

        self.kalman.in_heater_on = self.ctrl.heater_on
        self.kalman.in_T = self.noise_sensor.y

        self.save()
