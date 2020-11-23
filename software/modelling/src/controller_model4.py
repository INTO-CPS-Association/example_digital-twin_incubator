from oomodelling import Model
import time

class ControllerModel4(Model):
    def __init__(self, desired_temperature=45.0, lower_bound=8, upper_bound=8, heating_time = 3, heating_gap = 1):
        super().__init__()

        self.T_desired = self.parameter(desired_temperature)

        self.lower_bound = self.parameter(lower_bound)

        self.upper_bound = self.parameter(upper_bound)

        self.heating_time = self.parameter(heating_time)
        self.heating_gap = self.parameter(heating_gap)

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
        if in_temperature <= T_desired - self.lower_bound:
            self.cached_heater_on = True
            time.sleep(self.heating_time)
            self.cached_heater_on = False
            time.sleep(self.heating_gap)
            if in_temperature >= T_desired + self.upper_bound:
                self.cached_heater_on = False
            else:
                self.cached_heater_on = True
        else:
            self.cached_heater_on = False
            time.sleep(self.heating_gap)
            if in_temperature >= T_desired + self.upper_bound:
                self.cached_heater_on = False
            else:
                self.cached_heater_on = True
        return self.cached_heater_on