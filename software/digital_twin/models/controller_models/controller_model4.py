from oomodelling import Model
import time


class ControllerModel4(Model):
    def __init__(self, desired_temperature=45.0, lower_bound=5, heating_time=0.2, heating_gap=0.3):
        super().__init__()

        self.T_desired = self.parameter(desired_temperature)

        self.lower_bound = self.parameter(lower_bound)

        self.heating_time = self.parameter(heating_time)
        self.heating_gap = self.parameter(heating_gap)

        self.in_temperature = self.input(lambda: 20.0)

        self.current_state = "CoolingDown"
        self.next_time = -1.0
        self.cached_heater_on = False

        self.heater_on = self.var(lambda: self.cached_heater_on)

        self.save()

    def discrete_step(self):
        self.ctrl_step()
        return super().discrete_step()

    def ctrl_step(self):
        if self.current_state == "CoolingDown":
            # print("current state is: CoolingDown")
            self.cached_heater_on = False
            if self.in_temperature() <= self.T_desired - self.lower_bound:
                self.current_state = "Heating"
                self.next_time = self.time() + self.heating_time
            return
        if self.current_state == "Heating":
            # print("current state is: Heating")
            self.cached_heater_on = True
            if 0 < self.next_time <= self.time():
                self.current_state = "Waiting"
                self.next_time = self.time() + self.heating_gap
            return
        if self.current_state == "Waiting":
            # print("current state is: Waiting")
            self.cached_heater_on = False
            if 0 < self.next_time <= self.time():
                if self.in_temperature() <= self.T_desired:
                    self.current_state = "Heating"
                    # print("next state is heating from waiting")
                    self.next_time = self.time() + self.heating_time
                else:
                    self.current_state = "CoolingDown"
                    self.next_time = -1
            return
