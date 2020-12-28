from oomodelling import Model

from digital_twin.models.controller_models.controller_model4 import ControllerModel4
from digital_twin.models.plant_models.four_parameters_model.four_parameter_model import FourParameterIncubatorPlant


class SystemModel4Parameters(Model):
    def __init__(self, C_air,
                 G_box,
                 C_heater,
                 G_heater,
                 lower_bound=10, heating_time=0.2, heating_gap=2.0,
                 desired_temperature=35,
                 initial_box_temperature=35):
        super().__init__()

        self.ctrl = ControllerModel4(desired_temperature=desired_temperature, heating_time=heating_time, heating_gap=heating_gap,
                                     lower_bound=lower_bound)
        self.plant = FourParameterIncubatorPlant(initial_box_temperature=initial_box_temperature,
                                                 C_air=C_air,
                                                 G_box=G_box,
                                                 C_heater=C_heater,
                                                 G_heater=G_heater)

        self.ctrl.in_temperature = self.plant.T
        self.plant.in_heater_on = self.ctrl.heater_on

        self.save()
