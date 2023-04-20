from oomodelling import Model

from models.plant_models.globals import HEATER_VOLTAGE, HEATER_CURRENT
from models.plant_models.two_parameters_model.two_parameter_model import TwoParameterIncubatorPlant


class FourParameterIncubatorPlant(TwoParameterIncubatorPlant):
    def __init__(self,
                 initial_heat_voltage=HEATER_VOLTAGE, initial_heat_current=HEATER_CURRENT,
                 initial_room_temperature=21.0, initial_box_temperature=25.0,
                 initial_heat_temperature=25.0,
                 C_air=1.0, G_box=1.0,
                 C_heater=1.0, G_heater=1.0):

        # Initialize 2p stuff
        super(FourParameterIncubatorPlant, self).__init__(initial_heat_voltage, initial_heat_current,
                         initial_room_temperature, initial_box_temperature, C_air, G_box)

        self.edit() # Go into edit mode

        self.C_heater = self.parameter(C_heater)
        self.G_heater = self.parameter(G_heater)

        self.T_heater = self.state(initial_heat_temperature)

        self.power_transfer_heat = self.var(lambda: self.G_heater*(self.T_heater() - self.T()))

        self.total_power_heater = self.var(lambda: self.power_in() - self.power_transfer_heat())

        # Override equation of TwoParameterIncubatorPlant
        self.total_power_box = self.ovar(lambda: self.power_transfer_heat() - self.power_out_box())

        self.der('T_heater', lambda: (1.0/self.C_heater)*(self.total_power_heater()))

        self.save()  # Close edit mode
