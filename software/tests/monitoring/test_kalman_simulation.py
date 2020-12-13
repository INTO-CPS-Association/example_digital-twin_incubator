import unittest

import matplotlib.pyplot as plt
from oomodelling import ModelSolver

from digital_twin.monitoring.kalman_system_model import KalmanSystemModel
from tests.cli_mode_test import CLIModeTest


class TestKalmanSimulation(CLIModeTest):

    def test_kalman_4_param_model_variable_noise(self):
        step_size = 0.1
        std_dev = 0.1

        params = [486.1198196,  # C_air
                  0.85804919,  # G_box
                  33.65074598,  # C_heater
                  0.86572258]  # G_heater
        C_air_num = params[0]
        G_box_num = params[1]
        C_heater_num = params[2]
        G_heater_num = params[3]

        m = KalmanSystemModel(step_size, std_dev,
                              C_air=C_air_num,
                              G_box=G_box_num,
                              C_heater=C_heater_num,
                              G_heater=G_heater_num)

        ModelSolver().simulate(m, 0.0, 300, step_size)

        plt.figure()
        plt.plot(m.signals['time'], m.noise_sensor.signals['y'], label="sensor T")
        plt.plot(m.signals['time'], m.plant.signals['T'], label="real T")
        plt.plot(m.signals['time'], m.kalman.signals['out_T'], label="kalman T")
        plt.legend()

        plt.figure()
        plt.step(m.signals['time'], m.ctrl.signals['heater_on'])

        plt.figure()
        plt.plot(m.signals['time'], m.plant.signals['T_heater'], label="T_heater")
        plt.plot(m.signals['time'], m.kalman.signals['out_T_heater'], label="kalman T_heater")

        if self.ide_mode():
            plt.show()


if __name__ == '__main__':
    unittest.main()
