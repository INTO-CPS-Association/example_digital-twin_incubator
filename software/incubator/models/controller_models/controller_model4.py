from oomodelling import Model


class ControllerModel4(Model):
    def __init__(self, temperature_desired=45.0, lower_bound=10.0, heating_time=0.2, heating_gap=0.3):
        super().__init__()

        self.T_desired = self.parameter(temperature_desired)

        self.lower_bound = self.parameter(lower_bound)

        self.heating_time = self.parameter(heating_time)
        self.heating_gap = self.parameter(heating_gap)

        self.in_temperature = self.input(lambda: 20.0)

        self.state_machine = ControllerModel4SM(temperature_desired, lower_bound, heating_time, heating_gap)

        self.curr_state_model = self.var(lambda: self.state_machine.current_state)

        self.heater_on = self.var(lambda: self.state_machine.cached_heater_on)

        self.save()

    def discrete_step(self):
        self.ctrl_step()
        return super().discrete_step()

    def ctrl_step(self):
        self.state_machine.step(self.time(), self.in_temperature())


class ControllerModel4SM:
    def __init__(self, temperature_desired, lower_bound, heating_time, heating_gap):
        assert 0 < temperature_desired
        assert 0 < lower_bound
        assert 0 < heating_time
        assert 0 < heating_gap

        self.temperature_desired = temperature_desired
        self.lower_bound = lower_bound
        self.heating_time = heating_time
        self.heating_gap = heating_gap

        self.current_state = "CoolingDown"
        self.next_time = -1.0
        self.cached_heater_on = False

    def step(self, time, in_temperature):
        if self.current_state == "CoolingDown":
            self.cached_heater_on = False
            if in_temperature <= self.temperature_desired - self.lower_bound:
                self.current_state = "Heating"
                self.next_time = time + self.heating_time
            return
        if self.current_state == "Heating":
            self.cached_heater_on = True
            if 0 < self.next_time <= time:
                self.current_state = "Waiting"
                self.next_time = time + self.heating_gap
            elif in_temperature > self.temperature_desired:
                self.current_state = "CoolingDown"
                self.next_time = -1.0
            return
        if self.current_state == "Waiting":
            self.cached_heater_on = False
            if 0 < self.next_time <= time:
                if in_temperature <= self.temperature_desired:
                    self.current_state = "Heating"
                    # print("next state is heating from waiting")
                    self.next_time = time + self.heating_time
                else:
                    self.current_state = "CoolingDown"
                    self.next_time = -1
            return

