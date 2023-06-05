from oomodelling import Model

from incubator.models.controller_models.controller_model4 import ControllerModel4
from incubator.models.plant_models.four_parameters_model.four_parameter_model import FourParameterIncubatorPlant


class SystemModel4Parameters(Model):
    def __init__(self, C_air,
                 G_box,
                 C_heater,
                 G_heater,
                 V_heater,
                 I_heater,
                 lower_bound=10, heating_time=20, heating_gap=30,
                 temperature_desired=35,
                 initial_box_temperature=35,
                 initial_heat_temperature=35):
        super().__init__()

        self.ctrl = ControllerModel4(temperature_desired=temperature_desired, heating_time=heating_time,
                                     heating_gap=heating_gap,
                                     lower_bound=lower_bound)
        self.plant = FourParameterIncubatorPlant(V_heater, I_heater,
                                                 initial_box_temperature, initial_box_temperature,
                                                 initial_heat_temperature,
                                                 C_air, G_box,
                                                 C_heater, G_heater)

        self.ctrl.in_temperature = self.plant.T
        self.plant.in_heater_on = self.ctrl.heater_on

        self.save()
