import unittest

import matplotlib.pyplot as plt
from oomodelling import ModelSolver

from incubator.models.plant_models.four_parameters_model.best_parameters import four_param_model_params
from incubator.monitoring.kalman_system_model import KalmanSystemModel
from incubator.tests.cli_mode_test import CLIModeTest


class TestKalmanSimulation(CLIModeTest):

    def test_kalman_4_param_model_variable_noise(self):
        step_size = 0.5
        std_dev = 0.001
        Theater_covariance_init = T_covariance_init = 0.0002

        params = four_param_model_params
        C_air_num = params[0]
        G_box_num = params[1]
        C_heater_num = params[2]
        G_heater_num = params[3]

        m = KalmanSystemModel(step_size, std_dev,
                              Theater_covariance_init, T_covariance_init,
                              C_air_num,
                              G_box_num,
                              C_heater_num,
                              G_heater_num)

        ModelSolver().simulate(m, 0.0, 800, step_size, step_size/10.0)

        plt.figure()
        plt.plot(m.signals['time'], m.noise_sensor.signals['y'], label="sensor T")
        # plt.plot(m.signals['time'], m.plant.signals['T'], label="real T")
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
