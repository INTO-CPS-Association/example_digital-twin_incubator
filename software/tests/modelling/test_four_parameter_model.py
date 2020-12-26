import logging
import math
import unittest
from scipy.optimize import leastsq
import matplotlib.pyplot as plt
import sympy as sp

from digital_twin.data_processing.data_processing import load_data
from digital_twin.models.plant_models.four_parameters_model.best_parameters import four_param_model_params
from digital_twin.models.plant_models.model_functions import construct_residual, run_experiment_four_parameter_model, \
    run_experiment_two_parameter_model
from tests.cli_mode_test import CLIModeTest


class FourParameterModelTests(CLIModeTest):

    def test_calibrate_four_parameter_model(self):
        NEvals = 100 if self.ide_mode() else 1
        logging.basicConfig(level=logging.WARN)

        experiments = [
            "../datasets/controller_tunning/exp2_ht20_hg30.csv",
            # "../datasets/calibration_fan_24v/semi_random_movement.csv",
            # "../datasets/calibration_fan_12v/ramp_up_cool_down.csv",
            # "../datasets/calibration_fan_12v/random_on_off_sequences_1",
            # "../datasets/calibration_fan_12v/random_on_off_sequences_2"
        ]
        params = four_param_model_params

        tf = 1500 if self.ide_mode() else 30

        residual = construct_residual(experiments, run_exp=run_experiment_four_parameter_model,
                                      desired_timeframe=(-math.inf, tf), h=6.0)

        print(leastsq(residual, params, maxfev=NEvals))

    def test_run_experiment_four_parameter_model(self):
        params = four_param_model_params
        # CWD: Example_Digital-Twin_Incubator\software\
        data = load_data("../datasets/controller_tunning/exp2_ht20_hg30.csv",
                         desired_timeframe=(-math.inf, math.inf))
        results, sol = run_experiment_four_parameter_model(data, params)

        fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, 1)

        ax1.plot(data["time"], data["t1"], label="t1")
        ax1.plot(data["time"], data["t2"], label="t2")
        ax1.plot(data["time"], data["t3"], label="t3")
        ax1.plot(results.signals["time"], results.signals["T"], label="~T(4)")
        ax1.plot(data["time"], data["average_temperature"], label="average_temperature")
        ax1.plot(results.signals["time"], results.signals["in_room_temperature"], label="~roomT")
        ax1.plot(data["time"], [50 if b else 30 for b in data["heater_on"]], label="heater_on")
        ax1.legend()

        ax2.plot(results.signals["time"], results.signals["T_heater"], label="~T_heater")
        ax2.legend()

        ax3.plot(data["time"], data["heater_on"], label="heater_on")
        ax3.plot(data["time"], data["fan_on"], label="fan_on")
        ax3.plot(results.signals["time"], results.signals["in_heater_on"], label="~heater_on")
        ax3.legend()

        ax4.plot(data["time"], data["power_in"], label="power_in")
        ax4.plot(results.signals["time"], results.signals["power_in"], label="~power_in")
        ax4.legend()

        if self.ide_mode():
            plt.show()

    def test_run_experiment_compare_models(self):
        # If you run this experiment with the C_heater=1e-2 and G_heater=1e-2, then you will get the two models being mostly equivalent.
        params = four_param_model_params
        # CWD: Example_Digital-Twin_Incubator\software\
        data = load_data("../datasets/calibration_fan_24v/semi_random_movement.csv",
                         desired_timeframe=(-math.inf, 2000))

        results_4p, sol = run_experiment_four_parameter_model(data, params)

        params = [616.56464029,  # C_air
                  0.65001889]  # G_box

        results_2p, sol = run_experiment_two_parameter_model(data, params)

        fig, (ax1) = plt.subplots(1, 1)

        # ax1.plot(data["time"], data["t1"], label="t1")
        # ax1.plot(data["time"], data["t2"], label="t2")
        # ax1.plot(data["time"], data["t3"], label="t3")
        ax1.plot(results_2p.signals["time"], results_2p.signals["T"], label="~T(2)")
        ax1.plot(results_4p.signals["time"], results_4p.signals["T"], label="~T(4)")
        ax1.plot(results_4p.signals["time"], results_4p.signals["in_room_temperature"], label="~roomT")
        ax1.plot(data["time"], [50 if b else 30 for b in data["heater_on"]], label="heater_on")
        ax1.plot(data["time"], data["average_temperature"], label="average_temperature")
        ax1.legend()

        # ax2.plot(results_4p.signals["time"], results_4p.signals["T_heater"], label="~T_heater")
        # ax2.legend()
        #
        # ax3.plot(data["time"], data["heater_on"], label="heater_on")
        # ax3.plot(data["time"], data["fan_on"], label="fan_on")
        # ax3.plot(results_4p.signals["time"], results_4p.signals["in_heater_on"], label="~heater_on")
        # ax3.legend()
        #
        # ax4.plot(data["time"], data["power_in"], label="power_in")
        # ax4.plot(results_4p.signals["time"], results_4p.signals["power_in"], label="~power_in")
        # ax4.legend()

        # ax5.plot(data["time"], data["energy_in"], label="energy_in")
        # ax5.plot(data["time"], data["potential_energy"], label="potential_energy")
        # ax5.legend()

        if self.ide_mode():
            plt.show()

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

        der_T = (1.0 / C_air) * (total_power_box)
        der_T_heater = (1.0 / C_heater) * (total_power_heater)

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
