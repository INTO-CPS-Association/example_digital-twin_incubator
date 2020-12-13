from oomodelling import Model

from digital_twin.models.controller_models.controller_model4 import ControllerModel4
from digital_twin.models.plant_models.four_parameters_model.four_parameter_model import FourParameterIncubatorPlant
from digital_twin.monitoring.kalman_filter_4p import KalmanFilter4P
from digital_twin.monitoring.noise_model import NoiseFeedthrough


class KalmanSystemModel(Model):
    def __init__(self, step_size):
        super().__init__()

        self.ctrl = ControllerModel4(desired_temperature=35)
        self.plant = FourParameterIncubatorPlant()
        self.noise_sensor = NoiseFeedthrough()
        self.kalman = KalmanFilter4P(step_size)

        self.noise_sensor.u = self.plant.T
        self.ctrl.in_temperature = self.noise_sensor.y
        self.plant.in_heater_on = self.ctrl.heater_on

        self.kalman.in_heater_on = self.ctrl.heater_on
        self.kalman.in_T = self.noise_sensor.y

        self.save()
