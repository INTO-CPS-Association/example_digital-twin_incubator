from oomodelling.Model import Model


class Temperature(Model):
    def __init__(self):
        super().__init__()

        self.T = self.input(lambda: 20.0)

        self.save()


class ThermalConductor(Model):
    def __init__(self):
        super().__init__()

        self.Ta = self.input(lambda: 20.0)
        self.Tb = self.input(lambda: 20.0)

        self.dT = self.var(lambda: self.Ta() - self.Tb())

        self.G = self.parameter(1.0)

        self.QFlow = self.var(lambda: self.G * self.dT())

        self.save()


class ThermalCapacitor(Model):
    def __init__(self):
        super().__init__()

        self.T = self.state(20.0)
        self.QFlow = self.input(lambda: 1.0)

        self.C = self.parameter(1.0)

        self.der('T', lambda: (1.0 / self.C) * (self.QFlow()))

        self.save()


class ComplexIncubatorPlant(Model):
    def __init__(self, Tin, heatingG, airC, boxG, roomC):
        super().__init__()

        self.in_T = self.input(lambda: Tin)

        self.convection = ThermalConductor()
        self.convection.G = heatingG

        self.box_air = ThermalCapacitor()
        self.box_air.C = airC

        self.box = ThermalConductor()
        self.box.G = boxG

        self.room_air = ThermalCapacitor()
        self.room_air.C = roomC
        self.room_air.T = 24.0

        self.convection.Ta = self.in_T
        self.convection.Tb = self.box_air.T

        self.box_air.QFlow = lambda: (self.convection.QFlow() - self.box.QFlow())

        self.box.Ta = self.box_air.T
        self.box.Tb = self.room_air.T

        self.room_air.QFlow = self.box.QFlow

        self.save()


class IncubatorPlant(Model):
    def __init__(self, heatPow, roomT, airC, boxG):
        super().__init__()

        self.in_heater_power = self.input(lambda: heatPow)

        self.in_qflow = self.state(0.0)
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