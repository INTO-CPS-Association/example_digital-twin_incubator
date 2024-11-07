import logging
import math
import unittest

import matplotlib.pyplot as plt
import numpy as np
import sympy as sp
from scipy import integrate
from scipy.optimize import leastsq

from incubator.data_processing.data_processing import load_data, derive_data
from incubator.models.plant_models.model_functions import construct_residual, run_experiment_two_parameter_model
from incubator.physical_twin.low_level_driver_server import CTRL_EXEC_INTERVAL
from incubator.tests.cli_mode_test import CLIModeTest


class TestsModelling(CLIModeTest):

    def test_calibrate_two_parameter_model_20200918(self):
        NEvals = 100 if self.ide_mode() else 1
        logging.basicConfig(level=logging.INFO)

        # CWD: Example_Digital-Twin_Incubator\software\
        params = [
            498.71218224,  # C_air
            0.62551039,  # G_box
            10.917042,  # V_heater
            9.12718588,  # I_heater
        ]

        data, _ = load_data("./incubator/datasets/20200918_calibration_fan_24V/semi_random_movement.csv",
                            time_unit='s',
                            normalize_time=False,
                            convert_to_seconds=False)
        data = derive_data(data, V_heater=params[2], I_Heater=params[3],
                           avg_function=lambda row: np.mean([row.t2, row.t3]))
        data.rename(columns={"t1": "T_room"}, inplace=True)

        h = 2*CTRL_EXEC_INTERVAL

        def run_exp(params):
            m, sol = run_experiment_two_parameter_model(data, params, h=h)
            return m, sol, data

        residual = construct_residual([run_exp])

        leastsq(residual, np.array(params), maxfev=NEvals)


    def test_run_experiment_two_parameter_model_20200918(self):
        params = [
            498.71218224,  # C_air
            0.62551039,  # G_box
            10.917042,  # V_heater
            9.12718588,  # I_heater
        ]
        data, _ = load_data("./incubator/datasets/20200918_calibration_fan_24V/semi_random_movement.csv",
                            desired_timeframe=(-math.inf, math.inf))
        data = derive_data(data, V_heater=params[2], I_Heater=params[3],
                           avg_function=lambda row: np.mean([row.t2, row.t3]))
        data.rename(columns={"t1": "T_room"}, inplace=True)

        results, sol = run_experiment_two_parameter_model(data, params)

        fig, (ax1, ax2) = plt.subplots(2, 1)

        ax1.plot(data["time"], data["T_room"], label="T_room")
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

        if self.ide_mode():
            plt.show()
        plt.close(fig)

    def test_calibrate_two_parameter_model_20230501(self):
        logging.basicConfig(level=logging.INFO)

        NEvals = 100 if self.ide_mode() else 1

        data, _ = load_data("./incubator/datasets/20230501_calibration_empty_system/20230501_calibration_empty_system.csv",
                            time_unit='ns',
                            normalize_time=False,
                            convert_to_seconds=True)
        data.rename(columns={"t3": "T_room"}, inplace=True)

        params = [
            6.42171870e+02,  # C_air
            4.96056150e-01,  # G_box
            1.14165310e+01,  # V_heater
            1.42706637e+00,  # I_heater
        ]

        h = 2*CTRL_EXEC_INTERVAL

        def run_exp(params):
            m, sol = run_experiment_two_parameter_model(data, params, h=h)
            return m, sol, data

        residual = construct_residual([run_exp])

        leastsq(residual, np.array(params), maxfev=NEvals)

    def test_run_experiment_two_parameter_model_20230501(self):
        params = [
            6.42171870e+02,  # C_air
            4.96056150e-01,  # G_box
            1.14165310e+01,  # V_heater
            1.42706637e+00,  # I_heater
        ]
        data, _ = load_data(
            "./incubator/datasets/20230501_calibration_empty_system/20230501_calibration_empty_system.csv",
            time_unit='ns',
            normalize_time=False,
            convert_to_seconds=True)
        data.rename(columns={"t3": "T_room"}, inplace=True)

        results, sol = run_experiment_two_parameter_model(data, params)

        fig, (ax1, ax2) = plt.subplots(2, 1)

        ax1.plot(data["time"], data["T_room"], label="T_room")
        ax1.plot(results.signals["time"], results.signals["T"], label="~T")
        ax1.plot(results.signals["time"], results.signals["in_room_temperature"], label="~roomT")
        ax1.plot(data["time"], data["average_temperature"], label="average_temperature")
        ax1.legend()

        ax2.plot(data["time"], data["heater_on"], label="heater_on")
        ax2.plot(data["time"], data["fan_on"], label="fan_on")
        ax2.plot(results.signals["time"], results.signals["in_heater_on"], label="~heater_on")
        ax2.legend()

        if self.ide_mode():
            plt.show()
        plt.close(fig)


    def plot_compare_model_data(self, csv, title):
        params = [
            498.71218224,  # C_air
            0.62551039,  # G_box
            10.917042,  # V_heater
            9.12718588,  # I_heater
        ]
        V_heater = params[2]
        I_heater = params[3]
        data, _ = load_data(csv)
        data = derive_data(data, V_heater, I_heater, avg_function=lambda row: np.mean([row.t2, row.t3]))
        data.rename(columns={"t1": "T_room"}, inplace=True)
        data["power_in"] = data.apply(lambda row: V_heater * I_heater if row.heater_on else 0.0, axis=1)
        data["energy_in"] = data.apply(
            lambda row: integrate.trapezoid(data[0:row.name + 1]["power_in"], x=data[0:row.name + 1]["time"]), axis=1)

        results, _ = run_experiment_two_parameter_model(data, params, h=CTRL_EXEC_INTERVAL)

        fig, (ax1, ax2, ax3) = plt.subplots(3, 1)

        ax1.plot(data["time"], data["T_room"], label="T_room")
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

        plt.close(fig)

        return results, data

    def test_check_two_parameter_model_inputs(self):
        results, data = self.plot_compare_model_data(
            "./incubator/datasets/20200917_calibration_fan_12v/random_on_off_sequences.csv",
            "random_on_off_sequences")

        self.assertTrue(abs(len(results.signals["in_heater_on"]) - len(data["heater_on"]) < 10))


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
