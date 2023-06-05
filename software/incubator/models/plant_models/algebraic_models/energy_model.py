from oomodelling import Model



class EnergyModel(Model):
    def __init__(self, initial_heat_voltage, initial_heat_current,
                 C_air=700,  # j kg^-1 °K^-1
                 Volume = 0.03,  # m^3
                 T0 = 20.0  # °C
                 ):
        super().__init__()

        self.in_heater_on = self.input(lambda: False)
        self.in_heater_voltage = self.input(lambda: initial_heat_voltage)
        self.in_heater_current = self.input(lambda: initial_heat_current)

        self.power_in = self.var(
            lambda: self.in_heater_voltage() * self.in_heater_current() if self.in_heater_on() else 0.0)

        self.C = self.parameter(C_air)

        self.Volume = self.parameter(Volume)

        self.Vol_per_Weight = self.parameter(0.04 / 0.03)

        self.Mass = self.parameter(self.Vol_per_Weight * self.Volume)  # (Kg)

        self.T0 = self.parameter(T0)  # °C

        self.T0_k = self.var(lambda: T0 / (5.0 / 9.0) + 32.0)  # °F

        self.energy = self.state(Volume * self.T0_k() * self.C)  # J

        self.T_k = self.var(lambda: self.energy() / (self.Volume * self.C))

        self.T = self.var(lambda: (self.T_k() - 32.0) * (5.0 / 9.0) )

        self.der('energy', lambda: self.power_in())

        self.save()
