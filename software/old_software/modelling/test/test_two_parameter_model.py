import logging
import math
import unittest

import numpy
from scipy.optimize import leastsq

from data_processing import load_data, derive_data
import matplotlib.pyplot as plt

from functions import run_experiment_two_parameter_model, construct_residual, run_experiment_four_parameter_model


class TestsModelling(unittest.TestCase):

    def test_calibrate_two_parameter_model(self):
        NEvals = 1
        logging.basicConfig(level=logging.INFO)

        # CWD: H:\srcctrl\github\Example_Digital-Twin_Incubator\software\modelling\test
        experiments = [
            "../../../datasets/calibration_fan_24v/semi_random_movement.csv",
            # "../../../datasets/calibration_fan_12v/random_on_off_sequences",
            # "../../../datasets/calibration_fan_12v/random_on_off_sequences_1",
            # "../../../datasets/calibration_fan_12v/random_on_off_sequences_2"
            ]
        params = [616.56464029,  # C_air
                  0.65001889]  # G_box

        residual = construct_residual(experiments,
                                      run_exp=run_experiment_two_parameter_model,
                                      desired_timeframe=(-math.inf, 750))

        print(leastsq(residual, params, maxfev=NEvals))

    def test_run_experiment_two_parameter_model(self):
        params = [616.56464029,  # C_air
                  0.65001889]   # G_box
        # CWD: H:\srcctrl\github\Example_Digital-Twin_Incubator\software\modelling\test
        data = derive_data(load_data("../../../datasets/calibration_fan_24v/semi_random_movement.csv",
                                     desired_timeframe=(-math.inf, 4000)))
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

        # plt.show()

    def test_check_two_parameter_model_inputs(self):
        params = [800.0,  # C_air
                  0.3]  # G_box
        # CWD: H:\srcctrl\github\Example_Digital-Twin_Incubator\software\modelling\test
        data = derive_data(load_data("../../../datasets/calibration_fan_12v/random_on_off_sequences.csv"))
        results, sol = run_experiment_two_parameter_model(data, params, h=3.0)

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

        self.assertTrue(abs(len(results.signals["in_heater_on"]) - len(data["heater_on"]) < 10))
        comparable_length = min(len(results.signals["in_heater_on"]), len(data["heater_on"]))

        convert_bool = lambda bool_array: [1.0 if b else 0.0 for b in bool_array]
        least_squared_error = lambda a, b: sum(((numpy.array(a)[0:comparable_length] - numpy.array(b)[0:comparable_length]) ** 2))

        self.assertTrue(least_squared_error(convert_bool(data["heater_on"]), convert_bool(results.signals["in_heater_on"])) < 1.0)

        ax4.plot(data["time"], data["power_in"], label="power_in")
        ax4.plot(results.signals["time"], results.signals["power_in"], label="~power_in")
        ax4.legend()

        self.assertTrue(least_squared_error(data["power_in"],
                                            results.signals["power_in"]) < 1.0)

        # plt.show()


if __name__ == '__main__':
    unittest.main()
