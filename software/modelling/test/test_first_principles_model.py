import logging
import unittest

import numpy
from scipy.optimize import leastsq

from data_processing import load_data, derive_data
import matplotlib.pyplot as plt

from scipy import integrate

from functions import run_experiment, construct_residual


class TestsModelling(unittest.TestCase):

    def test_calibrate_model(self):
        NEvals = 100
        logging.basicConfig(level=logging.INFO)

        # CWD: H:\srcctrl\github\Example_Digital-Twin_Incubator\software\modelling\test
        experiments = [
            "../../../datasets/calibration/ramp_up_cool_down.csv",
            # "../../../datasets/calibration/random_on_off_sequences_1",
            # "../../../datasets/calibration/random_on_off_sequences_2"
            ]
        params = [546.72725922,  # C_air
                  0.67488101]  # G_box

        residual = construct_residual(experiments)

        print(leastsq(residual, params, maxfev=NEvals))

    def test_run_experiment(self):
        params = [638.35778306,  # C_air
                  0.77556735]  # G_box
        # CWD: H:\srcctrl\github\Example_Digital-Twin_Incubator\software\modelling\test
        data = derive_data(load_data("../../../datasets/calibration/ramp_up_cool_down.csv"))
        results, sol = run_experiment(data, params)

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

        # ax3.plot(data["time"], data["execution_interval"], label="execution_interval")
        # ax3.plot(data["time"], data["elapsed"], label="elapsed")
        # ax3.legend()

        ax4.plot(data["time"], data["power_in"], label="power_in")
        ax4.plot(results.signals["time"], results.signals["power_in"], label="~power_in")
        ax4.legend()

        # ax5.plot(data["time"], data["energy_in"], label="energy_in")
        # ax5.plot(data["time"], data["potential_energy"], label="potential_energy")
        # ax5.legend()

        plt.show()

    def test_check_model_inputs(self):
        params = [800.0,  # C_air
                  0.3]  # G_box
        # CWD: H:\srcctrl\github\Example_Digital-Twin_Incubator\software\modelling\test
        data = derive_data(load_data("../../../datasets/calibration/random_on_off_sequences.csv"))
        results, sol = run_experiment(data, params, h=3.0)

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

    def test_plot_data_default_setup(self):
        # CWD: H:\srcctrl\github\Example_Digital-Twin_Incubator\software\modelling\test
        data = load_data("../../../datasets/calibration/random_on_off_sequences.csv")

        data = derive_data(data)

        fig, (ax1, ax2, ax3, ax4, ax5) = plt.subplots(5, 1)

        ax1.plot(data["time"], data["t1"], label="t1")
        ax1.plot(data["time"], data["t2"], label="t2")
        ax1.plot(data["time"], data["t3"], label="t3")
        ax1.plot(data["time"], data["average_temperature"], label="average_temperature")
        ax1.legend()

        ax2.plot(data["time"], data["heater_on"], label="heater_on")
        ax2.plot(data["time"], data["fan_on"], label="fan_on")
        ax2.legend()

        ax3.plot(data["time"], data["execution_interval"], label="execution_interval")
        ax3.plot(data["time"], data["elapsed"], label="elapsed")
        ax3.legend()

        ax4.plot(data["time"], data["power_in"], label="power_in")
        ax4.legend()

        ax5.plot(data["time"], data["energy_in"], label="energy_in")
        ax5.plot(data["time"], data["potential_energy"], label="potential_energy")
        ax5.legend()

        plt.show()

    def test_plot_data_uniform_experiment(self):
        # CWD: H:\srcctrl\github\Example_Digital-Twin_Incubator\software\modelling\test
        data = load_data("../../../datasets/calibration/unitform_temperature.csv")

        data["power_in"] = data.apply(lambda row: 11.8 * 10.45 if row.heater_on else 0.0, axis = 1)

        data["energy_in"] = data.apply(lambda row: integrate.trapz(data[0:row.name+1]["power_in"], x=data[0:row.name+1]["time"]), axis=1)
        data["average_temperature"] = data.apply(lambda row: numpy.mean([row.t1, row.t2, row.t3]), axis=1)
        data["std_dev_temperature"] = data.apply(lambda row: numpy.std([row.t1, row.t2, row.t3]), axis=1)
        zero_kelvin = 273.15
        data["avg_temp_kelvin"] = data["average_temperature"] + zero_kelvin
        air_mass = 0.04 # Kg
        air_heat_capacity = 700 # (j kg^-1 °K^-1)

        data["potential_energy"] = data["avg_temp_kelvin"] * air_mass * air_heat_capacity
        data["potential_energy"] = data["potential_energy"] - data.iloc[0]["potential_energy"]

        fig, (ax1, ax2, ax3, ax4, ax5, ax6) = plt.subplots(6, 1)

        ax1.plot(data["time"], data["t1"], label="t1")
        ax1.plot(data["time"], data["t2"], label="t2")
        ax1.plot(data["time"], data["t3"], label="t3")
        ax1.plot(data["time"], data["average_temperature"], label="average_temperature")
        ax1.legend()

        ax2.plot(data["time"], data["heater_on"], label="heater_on")
        ax2.plot(data["time"], data["fan_on"], label="fan_on")
        ax2.legend()

        ax3.plot(data["time"], data["execution_interval"], label="execution_interval")
        ax3.plot(data["time"], data["elapsed"], label="elapsed")
        ax3.legend()

        ax4.plot(data["time"], data["power_in"], label="power_in")
        ax4.legend()

        ax5.plot(data["time"], data["std_dev_temperature"], label="std_dev_temperature")
        ax5.legend()

        ax6.plot(data["time"], data["energy_in"], label="energy_in")
        ax6.plot(data["time"], data["potential_energy"], label="potential_energy")
        ax6.legend()

        plt.show()




if __name__ == '__main__':
    unittest.main()
