import numpy as np
from oomodelling import Model

from calibration.calibrator import Calibrator
from self_adaptation.controller_optimizer import IControllerOptimizer
from interfaces.updateable_kalman_filter import IUpdateableKalmanFilter


class SelfAdaptationManager:
    def __init__(self, anomaly_threshold, ensure_anomaly_timer, gather_data_timer, cool_down_timer,
                 calibrator: Calibrator,
                 kalman_filter: IUpdateableKalmanFilter,
                 controller_optimizer: IControllerOptimizer):
        assert 0 < ensure_anomaly_timer
        assert 0 < gather_data_timer
        assert 0 < anomaly_threshold
        self.current_state = "Listening"
        self.anomaly_threshold = anomaly_threshold
        self.gather_data_timer = gather_data_timer
        self.cool_down_timer = cool_down_timer
        self.ensure_anomaly_timer = ensure_anomaly_timer
        self.temperature_residual_abs = 0.0
        self.anomaly_detected = False
        self.kalman_filter = kalman_filter
        self.controller_optimizer = controller_optimizer

        # Holds the next sample for which an action has to be taken.
        self.next_action_timer = -1
        self.calibrator = calibrator
        self.time_anomaly_start = -1.0

    def reset(self):
        self.current_state = "Listening"
        self.next_action_timer = -1
        self.anomaly_detected = False
        self.time_anomaly_start = -1.0

    def step(self, real_temperature, predicted_temperature, time_s, skip_anomaly_detection=False):
        self.temperature_residual_abs = np.absolute(real_temperature - predicted_temperature)

        if self.current_state == "Listening":
            assert not self.anomaly_detected
            assert self.next_action_timer < 0
            if skip_anomaly_detection:
                self.time_anomaly_start = time_s
                self.current_state = "GatheringData"
                self.next_action_timer = self.gather_data_timer
                self.anomaly_detected = True
            else:
                if self.temperature_residual_abs >= self.anomaly_threshold:
                    self.time_anomaly_start = time_s
                    self.next_action_timer = self.ensure_anomaly_timer
                    self.current_state = "EnsuringAnomaly"
            return
        if self.current_state == "EnsuringAnomaly":
            assert not self.anomaly_detected
            assert self.next_action_timer >= 0

            if self.next_action_timer > 0:
                self.next_action_timer -= 1

            if self.temperature_residual_abs < self.anomaly_threshold:
                self.reset()
                return

            if self.next_action_timer == 0:
                assert self.temperature_residual_abs >= self.anomaly_threshold
                self.current_state = "GatheringData"
                self.next_action_timer = self.gather_data_timer
                self.anomaly_detected = True
                return

            return
        if self.current_state == "GatheringData":
            assert self.anomaly_detected
            assert self.next_action_timer >= 0
            if self.next_action_timer > 0:
                self.next_action_timer -= 1
            if self.next_action_timer == 0:
                self.current_state = "Calibrating"
                self.next_action_timer = -1
            return
        if self.current_state == "Calibrating":
            assert self.time_anomaly_start >= 0.0
            assert self.time_anomaly_start <= time_s
            success, C_air, G_box, C_heater, G_heater = self.calibrator.calibrate(self.time_anomaly_start, time_s)
            if success:
                self.kalman_filter.update_parameters(C_air, G_box, C_heater, G_heater)
                self.controller_optimizer.optimize_controller()

                self.current_state = "CoolingDown"
                self.next_action_timer = self.cool_down_timer
                self.anomaly_detected = False
            return
        if self.current_state == "CoolingDown":
            assert not self.anomaly_detected
            assert self.next_action_timer >= 0
            if self.next_action_timer > 0:
                self.next_action_timer -= 1
            if self.next_action_timer == 0:
                self.reset()
            return


class SelfAdaptationModel(Model):
    def __init__(self,
                 manager: SelfAdaptationManager
                 ):
        super().__init__()

        self.in_reset = self.input(lambda: False)
        self.real_temperature = self.input(lambda: 0.0)
        self.predicted_temperature = self.input(lambda: 0.0)
        self.state_machine = manager

        self.anomaly_detected = self.var(lambda: self.state_machine.anomaly_detected)
        self.temperature_residual_abs = self.var(lambda: self.state_machine.temperature_residual_abs)

        self.save()

    def discrete_step(self):
        self.state_machine.step(self.real_temperature(), self.predicted_temperature(), self.time())
        return super().discrete_step()
