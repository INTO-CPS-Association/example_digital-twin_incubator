from oomodelling import Model

from controller_model import ControllerModel
from two_parameter_model import TwoParameterIncubatorPlant


class SystemModel(Model):
    def __init__(self):
        super().__init__()

        self.ctrl = ControllerModel()
        self.plant = TwoParameterIncubatorPlant()

        self.ctrl.in_temperature = self.plant.T
        self.plant.in_heater_on = self.ctrl.heater_on

        self.save()
