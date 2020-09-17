import unittest

import numpy

from data_processing import load_data, derive_data
import matplotlib.pyplot as plt

from scipy import integrate

from functions import run_experiment


class TestsModelling(unittest.TestCase):

    def test_calibrate_model(self):
        # CWD: H:\srcctrl\github\Example_Digital-Twin_Incubator\software\modelling\test
        experiments = [
            "../../../datasets/calibration/random_on_off_sequences",
            # "../../../datasets/calibration/random_on_off_sequences_1",
            # "../../../datasets/calibration/random_on_off_sequences_2"
            ]
        params = [1.0,  # C_air
                  1.0]  # G_box

        # print(minimize(error, params, method='BFGS', options={'maxiter': 1}))

    def test_run_experiment(self):
        params = [1.0,  # C_air
                  1.0]  # G_box
        # CWD: H:\srcctrl\github\Example_Digital-Twin_Incubator\software\modelling\test
        data = derive_data(load_data("../../../datasets/calibration/random_on_off_sequences.csv"))
        results = run_experiment(data, params)

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
