from oomodelling import Model


class IncubatorPlant(Model):
    def __init__(self, initial_heat_voltage=11.8, initial_heat_current=9.0, initial_room_temperature=25.0, initial_box_temperature=25.0,
                 airC, boxG):
        super().__init__()

        self.in_heater_on = self.input(lambda: False)
        self.in_heater_voltage = self.input(lambda: initial_heat_voltage)
        self.in_heater_current = self.input(lambda: initial_heat_current)
        self.in_room_temperature = self.input(lambda: initial_room_temperature)

        self.power_in = self.var(lambda: self.in_heater_voltage() * self.in_heater_current() if self.in_heater_on() else 0.0)

        self.T = self.state()

        self.power_out = self.var(lambda: self.)
        self.der('in_qflow', lambda: self.in_heater_power())

        self.box_air = ThermalCapacitor()
        self.box_air.C = airC

        self.box = ThermalConductor()
        self.box.G = boxG

        self.room_T = self.input(lambda: roomT)

        self.box_air.QFlow = lambda: (self.in_qflow() - self.box.QFlow())

        self.box.Ta = self.box_air.T
        self.box.Tb = self.room_T

        self.save()