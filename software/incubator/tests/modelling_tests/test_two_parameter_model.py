import logging
import math
import unittest

import numpy
from scipy.optimize import leastsq

import matplotlib.pyplot as plt

from incubator.data_processing.data_processing import load_data, derive_data
from incubator.models.plant_models.model_functions import construct_residual, run_experiment_two_parameter_model
from incubator.models.plant_models.two_parameters_model.best_parameters import two_param_model_params
from incubator.physical_twin.low_level_driver_server import CTRL_EXEC_INTERVAL
from incubator.tests.cli_mode_test import CLIModeTest
import sympy as sp


class TestsModelling(CLIModeTest):

    def test_calibrate_two_parameter_model(self):
        NEvals = 100 if self.ide_mode() else 1
        logging.basicConfig(level=logging.INFO)

        # CWD: Example_Digital-Twin_Incubator\software\

        data, _ = load_data("./incubator/datasets/calibration_fan_24v/semi_random_movement.csv",
                            time_unit='s',
                            normalize_time=False,
                            convert_to_seconds=False)

        params = two_param_model_params

        h = CTRL_EXEC_INTERVAL

        def run_exp(params):
            m, sol = run_experiment_two_parameter_model(data, params, h=h)
            return m, sol, data

        residual = construct_residual([run_exp])

        if self.ide_mode():
            print(leastsq(residual, params, maxfev=NEvals))

    def test_run_experiment_two_parameter_model(self):
        params = two_param_model_params
        # CWD: Example_Digital-Twin_Incubator\software\
        data, _ = load_data("./incubator/datasets/calibration_fan_24v/semi_random_movement.csv",
                                     desired_timeframe=(-math.inf, math.inf))
        results, sol = run_experiment_two_parameter_model(data, params)

        fig, (ax1, ax2, ax4) = plt.subplots(3, 1)

        ax1.plot(data["time"], data["t1"], label="t1")
        ax1.plot(data["time"], data["t2"], label="t2")
        ax1.plot(data["time"], data["t3"], label="t3")
        ax1.plot(results.signals["time"], results.signals["T"], label="~T")
        ax1.plot(results.signals["time"], results.signals["in_room_temperature"], label="~roomT")
        ax1.plot(data["time"], data["average_temperature"], label="average_temperature")
        ax1.legend()

        ax2.plot(data["time"], data["heater_on"], label="heater_on")
        ax2.plot(data["time"], data["fan_on"], label="fan_on")
        ax2.plot(results.signals["time"], results.signals["in_heater_on"], label="~heater_on")
        ax2.legend()

        ax4.plot(data["time"], data["power_in"], label="power_in")
        ax4.plot(results.signals["time"], results.signals["power_in"], label="~power_in")
        ax4.legend()

        if self.ide_mode():
            plt.show()

    def plot_compare_model_data(self, csv, title):
        params = two_param_model_params
        data, _ = load_data(csv)
        results, _ = run_experiment_two_parameter_model(data, params, h=CTRL_EXEC_INTERVAL)

        fig, (ax1, ax2, ax3) = plt.subplots(3, 1)

        ax1.plot(data["time"], data["t1"], label="t1")
        ax1.plot(data["time"], data["t2"], label="t2")
        ax1.plot(data["time"], data["t3"], label="t3")
        ax1.plot(results.signals["time"], results.signals["T"], label="~T")
        ax1.plot(results.signals["time"], results.signals["in_room_temperature"], label="~roomT")
        ax1.plot(data["time"], data["average_temperature"], label="average_temperature")
        ax1.legend()

        ax2.plot(data["time"], data["heater_on"], label="heater_on")
        # ax2.plot(data["time"], data["fan_on"], label="fan_on")
        ax2.plot(results.signals["time"], results.signals["in_heater_on"], label="~heater_on")
        ax2.legend()

        ax3.plot(data["time"], data["power_in"], label="power_in")
        ax3.plot(results.signals["time"], results.signals["power_in"], label="~power_in")
        ax3.legend()

        plt.title(title)

        if self.ide_mode():
            plt.show()

        return results, data

    def test_check_two_parameter_model_inputs(self):
        results, data = self.plot_compare_model_data(
            "./incubator/datasets/20200917_calibration_fan_12v/random_on_off_sequences.csv",
            "random_on_off_sequences"
        )

        self.assertTrue(abs(len(results.signals["in_heater_on"]) - len(data["heater_on"]) < 10))
        comparable_length = min(len(results.signals["in_heater_on"]), len(data["heater_on"]))

        convert_bool = lambda bool_array: [1.0 if b else 0.0 for b in bool_array]
        sum_squared_error = lambda a, b: sum(
            ((numpy.array(a)[0:comparable_length] - numpy.array(b)[0:comparable_length]) ** 2))

        error_heater_in = sum_squared_error(convert_bool(data["heater_on"]),
                                            convert_bool(results.signals["in_heater_on"]))
        # print(f"error_heater_in={error_heater_in}")
        self.assertTrue(error_heater_in < 1.0)

        error_power_in = sum_squared_error(data["power_in"], results.signals["power_in"])
        # print(f"error_power_in={error_power_in}")
        self.assertTrue(error_power_in < 1.0)

    def test_show_symbolic_equations(self):
        P_in = sp.symbols("P_in")
        P_out = sp.symbols("P_out")
        P_total = sp.symbols("P_total")

        m_air = sp.symbols("m_air")
        c_air = sp.symbols("c_air")  # Specific heat capacity

        C_air = m_air * c_air

        dT_dt = 1 / C_air * (P_in - P_out)
        if self.ide_mode():
            print(f"dT_dt = {dT_dt}")

        V_heater = sp.symbols("V_heater")  # Voltage of heater
        i_heater = sp.symbols("i_heater")  # Current of heater

        P_in_num = V_heater * i_heater  # Electrical power in

        G_out = sp.symbols("G_out")  # Coefficient of heat transfer through the styrofoam box.
        T = sp.symbols("T")  # Temperature in the box
        T_room = sp.symbols("T_room")  # Temperature in the room

        P_out_num = G_out * (T - T_room)

        dT_dt = dT_dt.subs(P_in, P_in_num).subs(P_out, P_out_num)

        if self.ide_mode():
            print(f"dT_dt = {dT_dt}")

if __name__ == '__main__':
    unittest.main()
