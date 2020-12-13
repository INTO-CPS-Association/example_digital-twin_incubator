import unittest

import matplotlib.pyplot as plt
from oomodelling import ModelSolver

from digital_twin.monitoring.kalman_system_model import KalmanSystemModel
from tests.cli_mode_test import CLIModeTest


class TestKalmanSimulation(CLIModeTest):

    def test_kalman_4_param_model(self):
        step_size = 0.01
        m = KalmanSystemModel(step_size)

        ModelSolver().simulate(m, 0.0, 10, step_size)

        plt.figure()
        plt.plot(m.signals['time'], m.noise_sensor.signals['y'], label="T")
        plt.plot(m.signals['time'], m.kalman.signals['outT'], label="~T")

        plt.figure()
        plt.step(m.signals['time'], m.ctrl.signals['heater_on'])

        if self.ide_mode():
            plt.show()








if __name__ == '__main__':
    unittest.main()
