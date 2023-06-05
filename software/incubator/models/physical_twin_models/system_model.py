from oomodelling import Model

from incubator.models.controller_models.controller_model4 import ControllerModel4
from incubator.models.plant_models.two_parameters_model.two_parameter_model import TwoParameterIncubatorPlant


class SystemModel(Model):
    def __init__(self, initial_heat_voltage, initial_heat_current,
                 initial_room_temperature, initial_box_temperature,
                 C_air, G_box):
        super().__init__()

        self.ctrl = ControllerModel4()
        self.plant = TwoParameterIncubatorPlant(initial_heat_voltage, initial_heat_current,
                 initial_room_temperature, initial_box_temperature,
                 C_air, G_box)

        self.ctrl.in_temperature = self.plant.T
        self.plant.in_heater_on = self.ctrl.heater_on

        self.save()
