from oomodelling import Model

from globals import HEATER_VOLTAGE, HEATER_CURRENT


class ControllerModel(Model):
    def __init__(self, temperature_lower_limit=15.0):
        super().__init__()

        self.TL = self.parameter(temperature_lower_limit)

        self.in_temperature = self.input(lambda: 20.0)

        self.heater_on = self.var(lambda: self.calculate_ctrl_action(self.TL, self.in_temperature()))

        self.save()

    def calculate_ctrl_action(self, tl, in_temperature):
        """
        Returns whether heater is on or not (true or false)
        """
        return True
