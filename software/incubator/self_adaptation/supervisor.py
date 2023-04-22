import numpy as np
from oomodelling import Model

from incubator.self_adaptation.controller_optimizer import ControllerOptimizer


class ISupervisorSM:
    def step(self, T, T_heater, time):
        raise NotImplementedError("For subclasses")


class SupervisorThresholdSM(ISupervisorSM):
    def __init__(self, controller_optimizer: ControllerOptimizer,
                 desired_temperature, max_t_heater,
                 trigger_optimization_threshold, heater_underused_threshold,
                 wait_til_supervising_timer):
        # Constants
        self.controller_optimizer = controller_optimizer
        self.desired_temperature = desired_temperature
        self.max_t_heater = max_t_heater
        self.trigger_optimization_threshold = trigger_optimization_threshold
        self.heater_underused_threshold = heater_underused_threshold
        self.wait_til_supervising_timer = wait_til_supervising_timer

        # Holds the next sample for which an action has to be taken.
        self.next_action_timer = -1
        self.current_state = None
        self.reset()

    def reset(self):
        self.next_action_timer = self.wait_til_supervising_timer
        self.current_state = "Waiting"

    def step(self, T, T_heater, time):
        if self.current_state == "Waiting":
            assert self.next_action_timer >= 0
            if self.next_action_timer > 0:
                self.next_action_timer -= 1

            if self.next_action_timer == 0:
                self.current_state = "Listening"
                self.next_action_timer = -1
            return
        if self.current_state == "Listening":
            assert self.next_action_timer < 0
            heater_safe = T_heater < self.max_t_heater
            heater_underused = (self.max_t_heater - T_heater) > self.heater_underused_threshold
            temperature_residual_above_threshold = np.absolute(T - self.desired_temperature) > self.trigger_optimization_threshold
            if heater_safe and heater_underused and temperature_residual_above_threshold:
                # Reoptimize controller and then go into waiting
                self.controller_optimizer.optimize_controller()
                self.reset()
                return
            else:
                pass  # Remain in listening and keep checking for deviations.
            return


class SupervisorPeriodicSM(ISupervisorSM):
    def __init__(self, controller_optimizer: ControllerOptimizer, wait_til_supervising_timer):
        # Constants
        self.controller_optimizer = controller_optimizer
        self.wait_til_supervising_timer = wait_til_supervising_timer

        # Holds the next sample for which an action has to be taken.
        self.next_action_timer = -1
        self.current_state = None
        self.reset()

    def reset(self):
        self.next_action_timer = self.wait_til_supervising_timer
        self.current_state = "Waiting"

    def step(self, T, T_heater, time):
        if self.current_state == "Waiting":
            assert self.next_action_timer >= 0
            if self.next_action_timer > 0:
                self.next_action_timer -= 1

            if self.next_action_timer == 0:
                # Reoptimize controller and then go into waiting again
                self.controller_optimizer.optimize_controller()
                self.reset()
            return


class SupervisorModel(Model):
    def __init__(self, sm: ISupervisorSM):
        super().__init__()

        self.state_machine = sm

        self.T = self.input(lambda: 0.0)
        self.T_heater = self.input(lambda: 0.0)

        self.save()

    def discrete_step(self):
        self.state_machine.step(self.T(), self.T_heater(), self.time())
        return super().discrete_step()
