from oomodelling import Model

from globals import HEATER_VOLTAGE, HEATER_CURRENT


class FourParameterIncubatorPlant(Model):
    def __init__(self,
                 initial_heat_voltage=HEATER_VOLTAGE, initial_heat_current=HEATER_CURRENT,
                 initial_room_temperature=25.0, initial_box_temperature=25.0,
                 initial_heat_temperature=25.0,
                 C_air=1.0, G_box=1.0,
                 C_heater=1.0, G_heater=1.0):
        super().__init__()

        self.in_heater_on = self.input(lambda: False)
        self.in_heater_voltage = self.input(lambda: initial_heat_voltage)
        self.in_heater_current = self.input(lambda: initial_heat_current)
        self.in_room_temperature = self.input(lambda: initial_room_temperature)

        self.power_in = self.var(lambda: self.in_heater_voltage() * self.in_heater_current() if self.in_heater_on() else 0.0)

        self.C_air = self.parameter(C_air)
        self.G_box = self.parameter(G_box)

        self.C_heater = self.parameter(C_heater)
        self.G_heater = self.parameter(G_heater)

        self.T = self.state(initial_box_temperature)
        self.T_heater = self.state(initial_heat_temperature)

        self.power_transfer_heat = self.var(lambda: self.G_heater*(self.T_heater() - self.T()))

        self.total_power_heater = self.var(lambda: self.power_in() - self.power_transfer_heat())

        self.power_out_box = self.var(lambda: self.G_box*(self.T() - self.in_room_temperature()))

        self.total_power_box = self.var(lambda: self.power_transfer_heat() - self.power_out_box())

        self.der('T', lambda: (1.0/self.C_air)*(self.total_power_box()))
        self.der('T_heater', lambda: (1.0/self.C_heater)*(self.total_power_heater()))

        self.save()