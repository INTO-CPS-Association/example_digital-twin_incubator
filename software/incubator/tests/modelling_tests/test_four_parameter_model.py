import logging
import math
import unittest

import numpy as np
from scipy.optimize import leastsq, least_squares
import matplotlib.pyplot as plt
import sympy as sp

from incubator.data_processing.data_processing import load_data, derive_data
from incubator.models.plant_models.model_functions import construct_residual, run_experiment_four_parameter_model, \
    run_experiment_two_parameter_model
from incubator.tests.cli_mode_test import CLIModeTest

l = logging.getLogger("FourParameterModelTests")


class FourParameterModelTests(CLIModeTest):

    def setUp(self) -> None:
        logging.basicConfig(level=(logging.INFO if self.ide_mode() else logging.WARN))

    def test_calibrate_four_parameter_model_20201221(self):
        NEvals = 500 if self.ide_mode() else 1

        params = [
            177.62927865,  # C_air
            0.77307655,  # G_box
            239.61236331,  # C_heater
            2.31872819,  # G_heater
            12.16,  # V_heater
            10.45,  # I_heater
        ]

        data, _ = load_data("./incubator/datasets/20201221_controller_tunning/exp2_ht20_hg30.csv",
                            time_unit='s',
                            normalize_time=False,
                            convert_to_seconds=False)
        data = derive_data(data, V_heater=params[4], I_Heater=params[5],
                           avg_function=lambda row: np.mean([row.t2, row.t3]))

        # Rename column to make data independent of specific tN's
        data.rename(columns={"t1": "T_room"}, inplace=True)

        h = 6.0

        def run_exp(params):
            m, sol = run_experiment_four_parameter_model(data, params, h=h)
            return m, sol, data

        residual = construct_residual([run_exp])

        l.info(leastsq(residual, np.array(params), maxfev=NEvals))

    def test_calibrate_four_parameter_model_20230501(self):
        NEvals = 500 if self.ide_mode() else 1

        params = [
            267.55929458,  # C_air
            0.5763498,  # G_box
            329.25376821,  # C_heater
            1.67053237,  # G_heater
            12.15579391,  # V_heater
            1.53551347  # I_heater
        ]

        data, _ = load_data(
            "./incubator/datasets/20230501_calibration_empty_system/20230501_calibration_empty_system.csv",
            time_unit='ns',
            normalize_time=False,
            convert_to_seconds=True)
        # Rename column to make data independent of specific tN's
        data.rename(columns={"t3": "T_room"}, inplace=True)
        h = 6.0

        def run_exp(params):
            m, sol = run_experiment_four_parameter_model(data, params, h=h)
            return m, sol, data

        residual = construct_residual([run_exp])

        l.info(least_squares(residual, params,
                             bounds=([0, 0, 0, 0, 12.15, 1.53], [300, 2.0, 500, 4, 12.17, 1.55]),
                             max_nfev=NEvals))

    def test_run_experiment_four_parameter_model_20201221(self):
        params = [
            177.62927865,  # C_air
            0.77307655,  # G_box
            239.61236331,  # C_heater
            2.31872819,  # G_heater
            12.16,  # V_heater
            10.45,  # I_heater
        ]

        # params[0]=0.6*params[0]

        # CWD: Example_Digital-Twin_Incubator\software\
        data, _ = load_data("./incubator/datasets/20201221_controller_tunning/exp2_ht20_hg30.csv",
                            time_unit='s',
                            normalize_time=False,
                            convert_to_seconds=False)
        data = derive_data(data, V_heater=params[4], I_Heater=params[5],
                           avg_function=lambda row: np.mean([row.t2, row.t3]))
        # Rename column to make data independent of specific tN's
        data.rename(columns={"t1": "T_room"}, inplace=True)

        results, sol = run_experiment_four_parameter_model(data, params)

        fig, (ax1, ax2, ax3) = plt.subplots(3, 1)
        # fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, 1)

        # ax1.plot(data["time"], data["t1"], label="t1")
        # ax1.plot(data["time"], data["t2"], label="t2")
        # ax1.plot(data["time"], data["t3"], label="t3")
        ax1.plot(data["time"], data["average_temperature"], label="average_temperature")
        ax1.plot(results.signals["time"], results.signals["T"], linestyle="dashed", label="~T(4)")
        # ax1.plot(results.signals["time"], results.signals["in_room_temperature"], label="~roomT")
        # ax1.plot(data["time"], [50 if b else 30 for b in data["heater_on"]], label="heater_on")
        ax1.legend()

        ax2.plot(results.signals["time"], results.signals["T_heater"], label="~T_heater")
        ax2.legend()

        ax3.plot(data["time"], data["heater_on"], label="heater_on")
        # ax3.plot(data["time"], data["fan_on"], label="fan_on")
        # ax3.plot(results.signals["time"], results.signals["in_heater_on"], label="~heater_on")
        ax3.legend()

        # ax4.plot(data["time"], data["power_in"], label="power_in")
        # ax4.plot(results.signals["time"], results.signals["power_in"], label="~power_in")
        # ax4.legend()

        if self.ide_mode():
            plt.show()

    def test_run_experiment_four_parameter_model_20230501(self):
        params = [267.55929458,  # C_air
                  0.5763498,  # G_box
                  329.25376821,  # C_heater
                  1.67053237,  # G_heater
                  12.15579391,  # V_heater
                  1.53551347]  # I_heater

        # params[0]=0.6*params[0]

        # CWD: Example_Digital-Twin_Incubator\software\
        data, _ = load_data(
            "./incubator/datasets/20230501_calibration_empty_system/20230501_calibration_empty_system.csv",
            time_unit='ns',
            normalize_time=False,
            convert_to_seconds=True)
        data = derive_data(data, V_heater=params[4], I_Heater=params[5],
                           avg_function=lambda row: np.mean([row.t2, row.t3]))
        # Rename column to make data independent of specific tN's
        data.rename(columns={"t3": "T_room"}, inplace=True)

        results, sol = run_experiment_four_parameter_model(data, params)

        fig, (ax1, ax2, ax3) = plt.subplots(3, 1)
        # fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, 1)

        # ax1.plot(data["time"], data["t1"], label="t1")
        # ax1.plot(data["time"], data["t2"], label="t2")
        # ax1.plot(data["time"], data["t3"], label="t3")
        ax1.plot(data["time"], data["average_temperature"], label="average_temperature")
        ax1.plot(results.signals["time"], results.signals["T"], linestyle="dashed", label="~T(4)")
        # ax1.plot(results.signals["time"], results.signals["in_room_temperature"], label="~roomT")
        # ax1.plot(data["time"], [50 if b else 30 for b in data["heater_on"]], label="heater_on")
        ax1.legend()

        ax2.plot(results.signals["time"], results.signals["T_heater"], label="~T_heater")
        ax2.legend()

        ax3.plot(data["time"], data["heater_on"], label="heater_on")
        # ax3.plot(data["time"], data["fan_on"], label="fan_on")
        # ax3.plot(results.signals["time"], results.signals["in_heater_on"], label="~heater_on")
        ax3.legend()

        # ax4.plot(data["time"], data["power_in"], label="power_in")
        # ax4.plot(results.signals["time"], results.signals["power_in"], label="~power_in")
        # ax4.legend()

        if self.ide_mode():
            plt.show()

    def test_run_experiment_compare_models(self):
        # If you run this experiment with the C_heater=1e-2 and G_heater=1e-2, then you will get the two models being mostly equivalent.
        params = [
            177.62927865,  # C_air
            0.77307655,  # G_box
            239.61236331,  # C_heater
            2.31872819,  # G_heater
            12.16,  # V_heater
            10.45,  # I_heater
        ]
        # CWD: Example_Digital-Twin_Incubator\software\
        data, _ = load_data("./incubator/datasets/20201221_controller_tunning/exp2_ht20_hg30.csv",
                            desired_timeframe=(-math.inf, math.inf))
        data = derive_data(data, V_heater=params[4], I_Heater=params[5],
                           avg_function=lambda row: np.mean([row.t2, row.t3]))
        # Rename column to make data independent of specific tN's
        data.rename(columns={"t1": "T_room"}, inplace=True)

        results_4p, sol_4p = run_experiment_four_parameter_model(data, params)

        params = [
            616.56464029,  # C_air
            0.65001889,  # G_box
            12.0,  # V_heater
            10.0,  # I_heater
        ]

        results_2p, sol_2p = run_experiment_two_parameter_model(data, params)

        fig, (ax1) = plt.subplots(1, 1)

        ax1.plot(results_2p.signals["time"], results_2p.signals["T"], label="~T(2)")
        ax1.plot(results_4p.signals["time"], results_4p.signals["T"], label="~T(4)")
        ax1.plot(results_4p.signals["time"], results_4p.signals["in_room_temperature"], label="~roomT")
        ax1.plot(data["time"], [50 if b else 30 for b in data["heater_on"]], label="heater_on")
        ax1.plot(data["time"], data["average_temperature"], label="average_temperature")
        ax1.legend()

        # Add data to dataframe, in case we want to export it.
        data["2P_Model"] = sol_2p.y[1, :]
        data["4P_Model"] = sol_4p.y[1, :]

        if self.ide_mode():
            plt.show()
            data.to_csv("exported_exp2_ht20_hg30.csv", sep=',')

    def test_show_symbolic_equations(self):
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

        der_T = (1.0 / C_air) * total_power_box
        der_T_heater = (1.0 / C_heater) * total_power_heater

        # Turn above into a linear system
        """
        States are:
        [[ T_heater ]
         [ T        ]]
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


if __name__ == '__main__':
    unittest.main()
