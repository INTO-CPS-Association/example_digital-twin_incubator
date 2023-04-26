from oomodelling import Model

from incubator.models.controller_models.controller_model_sm import ControllerModel4SM


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

