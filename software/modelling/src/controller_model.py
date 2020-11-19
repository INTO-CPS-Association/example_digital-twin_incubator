from oomodelling import Model

from globals import HEATER_VOLTAGE, HEATER_CURRENT


class ControllerModel(Model):
    def __init__(self, desired_temperature=45.0):
        super().__init__()

        self.T_desired = self.parameter(desired_temperature)

        self.in_temperature = self.input(lambda: 20.0)

        self.cached_heater_on = False

        self.heater_on = self.var(lambda: self.cached_heater_on)

        self.save()

    def discrete_step(self):
        self.cached_heater_on = self.calculate_ctrl_action(self.T_desired, self.in_temperature())
        return super().discrete_step()

    def calculate_ctrl_action(self, T_desired, in_temperature):
        """
        Returns whether heater is on or not (true or false)
        """
        if T_desired >= in_temperature:
            self.cached_heater_on = True
        else:
            self.cached_heater_on = False
        return self.cached_heater_on



