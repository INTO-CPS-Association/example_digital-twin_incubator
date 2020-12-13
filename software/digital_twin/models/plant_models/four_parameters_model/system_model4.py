from oomodelling import Model

from digital_twin.models.controller_models.controller_model4 import ControllerModel4
from digital_twin.models.plant_models.four_parameters_model.four_parameter_model import FourParameterIncubatorPlant


class SystemModel4Parameters(Model):
    def __init__(self):
        super().__init__()

        self.ctrl = ControllerModel4(desired_temperature=35)
        self.plant = FourParameterIncubatorPlant()

        self.ctrl.in_temperature = self.plant.T
        self.plant.in_heater_on = self.ctrl.heater_on

        self.save()


