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

        params = [
            177.62927865,  # C_air
            0.77307655,  # G_box
            239.61236331,  # C_heater
            2.31872819,  # G_heater
            12.16,  # V_heater
            10.45,  # I_heater
        ]
        C_air = params[0]
        G_box = params[1]
        C_heater = params[2]
        G_heater = params[3]
        V_heater = params[4]
        I_heater = params[5]

        m = KalmanSystemModel(step_size, std_dev,
                              Theater_covariance_init, T_covariance_init,
                              C_air,
                              G_box,
                              C_heater,
                              G_heater, V_heater, I_heater,
                              initial_room_temperature=21.0,
                              initial_box_temperature=21.0,
                              initial_heat_temperature=21.0)

        ModelSolver().simulate(m, 0.0, 800, step_size, step_size/10.0)

        fig1 = plt.figure()
        plt.plot(m.signals['time'], m.noise_sensor.signals['y'], label="sensor T")
        # plt.plot(m.signals['time'], m.plant.signals['T'], label="real T")
        plt.plot(m.signals['time'], m.kalman.signals['out_T'], label="kalman T")
        plt.legend()

        fig2 = plt.figure()
        plt.step(m.signals['time'], m.ctrl.signals['heater_on'])

        fig3 = plt.figure()
        plt.plot(m.signals['time'], m.plant.signals['T_heater'], label="T_heater")
        plt.plot(m.signals['time'], m.kalman.signals['out_T_heater'], label="kalman T_heater")

        if self.ide_mode():
            plt.show()
        plt.close(fig1)
        plt.close(fig2)
        plt.close(fig3)


if __name__ == '__main__':
    unittest.main()
