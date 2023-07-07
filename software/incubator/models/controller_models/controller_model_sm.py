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
        self.actuator_effort = 0

    def step(self, time, in_temperature):
        if self.current_state == "CoolingDown":
            assert self.cached_heater_on is False
            if in_temperature <= self.temperature_desired - self.lower_bound:
                self.current_state = "Heating"
                self.cached_heater_on = True
                self.actuator_effort += 1
                self.next_time = time + self.heating_time
            return
        if self.current_state == "Heating":
            assert self.cached_heater_on is True
            if 0 < self.next_time <= time:
                self.current_state = "Waiting"
                self.cached_heater_on = False
                self.actuator_effort += 1
                self.next_time = time + self.heating_gap
            elif in_temperature > self.temperature_desired:
                self.current_state = "CoolingDown"
                self.cached_heater_on = False
                self.actuator_effort += 1
                self.next_time = -1.0
            return
        if self.current_state == "Waiting":
            assert self.cached_heater_on is False
            if 0 < self.next_time <= time:
                if in_temperature <= self.temperature_desired:
                    self.current_state = "Heating"
                    self.cached_heater_on = True
                    self.actuator_effort += 1
                    self.next_time = time + self.heating_time
                else:
                    self.current_state = "CoolingDown"
                    self.cached_heater_on = False
                    self.next_time = -1
            return
