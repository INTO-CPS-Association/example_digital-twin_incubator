import math
import unittest
import sympy as sp
from control import ss
from filterpy.common import Q_discrete_white_noise
from filterpy.kalman import KalmanFilter

from digital_twin.data_processing.data_processing import load_data
from digital_twin.models.plant_models.globals import HEATER_VOLTAGE, HEATER_CURRENT
from digital_twin.models.plant_models.model_functions import run_experiment_four_parameter_model
from digital_twin.visualization.data_plotting import plotly_incubator_data, show_plotly
from tests.cli_mode_test import CLIModeTest
import numpy as np
import matplotlib.pyplot as plt


class TestKalmanFilter(CLIModeTest):

    def test_kalman_4_param_model(self):
        # Parameters
        C_air = sp.symbols("C_air")  # Specific heat capacity
        G_box = sp.symbols("G_box")  # Specific heat capacity
        C_heater = sp.symbols("C_heater")  # Specific heat capacity
        G_heater = sp.symbols("G_heater")  # Specific heat capacity

        # Constants
        V_heater = sp.symbols("V_heater")
        i_heater = sp.symbols("i_heater")

        # Inputs
        in_room_temperature = sp.symbols("T_room")
        on_heater = sp.symbols("on_heater")

        # States
        T = sp.symbols("T")
        T_heater = sp.symbols("T_h")

        power_in = on_heater * V_heater * i_heater

        power_transfer_heat = G_heater * (T_heater - T)

        total_power_heater = power_in - power_transfer_heat

        power_out_box = G_box * (T - in_room_temperature)

        total_power_box = power_transfer_heat - power_out_box

        der_T = (1.0 / C_air) * (total_power_box)
        der_T_heater = (1.0 / C_heater) * (total_power_heater)

        # Turn above into a CT linear system
        """
        States are:
        [[ T_heater ]
         [ T        ]]
         
        Inputs are: 
        [ [ on_heater ], 
          [ in_room_temperature ]]
        """
        A = sp.Matrix([
            [der_T_heater.diff(T_heater), der_T_heater.diff(T)],
            [der_T.diff(T_heater), der_T.diff(T)]
        ])

        B = sp.Matrix([
            [der_T_heater.diff(on_heater), der_T_heater.diff(in_room_temperature)],
            [der_T.diff(on_heater), der_T.diff(in_room_temperature)]
        ])

        # Observation matrix: only T can be measured
        C = sp.Matrix([[0.0, 1.0]])

        if self.ide_mode():
            print(f"dTh_dt = {der_T_heater}")
            print(f"dT_dt = {der_T}")
            print(f"A:")
            print(A)
            print(f"B:")
            print(B)
            print(f"C:")
            print(C)

        # Replace constants and get numerical matrices
        params = [486.1198196,  # C_air
                  0.85804919,  # G_box
                  33.65074598,  # C_heater
                  0.86572258]  # G_heater
        C_air_num = params[0]
        G_box_num = params[1]
        C_heater_num = params[2]
        G_heater_num = params[3]

        def replace_constants(m):
            return np.array(m.subs({
                        V_heater: HEATER_VOLTAGE,
                        i_heater: HEATER_CURRENT,
                        C_air: C_air_num,
                        G_box: G_box_num,
                        C_heater: C_heater_num,
                        G_heater: G_heater_num
                    })).astype(np.float64)

        A_num, B_num, C_num = map(replace_constants, [A, B, C])

        if self.ide_mode():
            print(A_num)
            print(B_num)
            print(C_num)

        data_sample_size = 3.0

        ct_system = ss(A_num, B_num, C_num, np.array([[0.0, 0.0]]))
        dt_system = ct_system.sample(data_sample_size, method="backward_diff")
        if self.ide_mode():
            print(ct_system)
            print(dt_system)

        # Load the data
        tf = 800.0
        # tf = 2000.0
        data = load_data("../datasets/calibration_fan_24v/semi_random_movement.csv",
                         desired_timeframe=(- math.inf, tf))

        time = data["time"]

        # Inputs to model
        measurements_heater = np.array([1.0 if b else 0.0 for b in data["heater_on"]])
        measurements_Troom = data["t1"].to_numpy()

        # System state
        measurements_T = data["average_temperature"].to_numpy()

        std_dev = 0.00001

        f = KalmanFilter(dim_x=2, dim_z=1, dim_u=2)
        f.x = np.array([[data.iloc[0]["average_temperature"]],  # T_heater at t=0
                        [data.iloc[0]["average_temperature"]]])  # T at t=0
        f.F = dt_system.A
        f.B = dt_system.B
        f.H = dt_system.C
        f.P = np.array([[100., 0.],
                        [0., 100.]])
        f.R = np.array([[std_dev]])
        f.Q = Q_discrete_white_noise(dim=2, dt=data_sample_size, var=std_dev ** 2)

        kalman_prediction = []
        for i in range(len(measurements_heater)):
            f.predict(u=np.array([
                [measurements_heater[i]],
                [measurements_Troom[i]]
            ]))
            f.update(np.array([[measurements_T[i]]]))
            kalman_prediction.append(f.x)

        kalman_prediction = np.array(kalman_prediction).squeeze(2)

        # Run experiment with model, without any filtering, just for comparison.
        results_4p, sol = run_experiment_four_parameter_model(data, params)

        fig = plotly_incubator_data(data, compare_to={
                                            "4pModel": {
                                                "time": results_4p.signals["time"],
                                                "T": results_4p.signals["T"],
                                            },
                                            "Kalman": {
                                                "time": time,
                                                "T": kalman_prediction[:, 1]
                                            },
                                        },
                                    heater_T_data = {
                                        "4pModel": {
                                            "time": results_4p.signals["time"],
                                            "T_heater": results_4p.signals["T_heater"],
                                        },
                                        "Kalman": {
                                            "time": time,
                                            "T_heater": kalman_prediction[:, 0]
                                        },
                                    },
                                    overlay_heater=True)

        if self.ide_mode():
            show_plotly(fig)

        # plt.figure()
        # plt.plot(time, kalman_prediction[:, 0], label="~T_heater")
        # plt.plot(time, kalman_prediction[:, 1], label="~T")
        # plt.plot(time, measurements_T, label="T")
        #
        # plt.legend()
        #
        # if self.ide_mode():
        #     plt.show()








if __name__ == '__main__':
    unittest.main()
