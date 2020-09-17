import unittest

import numpy

from data_processing import load_data
import matplotlib.pyplot as plt

from scipy import integrate


class MyTestCase(unittest.TestCase):

    def test_plot_data_default_setup(self):
        # CWD: H:\srcctrl\github\Example_Digital-Twin_Incubator\software\modelling\test
        data = load_data("../../digital_twin/diagnostics/output.csv")

        data["power_in"] = data.apply(lambda row: 11.8 * 10.45 if row.heater_on else 0.0, axis = 1)

        data["energy_in"] = data.apply(lambda row: integrate.trapz(data[0:row.name+1]["power_in"], x=data[0:row.name+1]["time"]), axis=1)
        data["average_temperature"] = data.apply(lambda row: numpy.mean([row.t0, row.t1, row.t2]), axis=1)
        data["std_dev_temperature"] = data.apply(lambda row: numpy.std([row.t0, row.t1, row.t2]), axis=1)
        zero_kelvin = 273.15
        data["avg_temp_kelvin"] = data["average_temperature"] + zero_kelvin
        air_mass = 0.04 # Kg
        air_heat_capacity = 700 # (j kg^-1 °K^-1)

        data["potential_energy"] = data["avg_temp_kelvin"] * air_mass * air_heat_capacity
        data["potential_energy"] = data["potential_energy"] - data.iloc[0]["potential_energy"]

        fig, (ax1, ax2, ax3, ax4, ax5, ax6) = plt.subplots(6, 1)

        ax1.plot(data["time"], data["t0"], label="t0")
        ax1.plot(data["time"], data["t1"], label="t1")
        ax1.plot(data["time"], data["t2"], label="t2")
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

    def test_plot_data_uniform_experiment(self):
        # CWD: H:\srcctrl\github\Example_Digital-Twin_Incubator\software\modelling\test
        data = load_data("../../../datasets/calibration/unitform_temperature.csv")

        data["power_in"] = data.apply(lambda row: 11.8 * 10.45 if row.heater_on else 0.0, axis = 1)

        data["energy_in"] = data.apply(lambda row: integrate.trapz(data[0:row.name+1]["power_in"], x=data[0:row.name+1]["time"]), axis=1)
        data["average_temperature"] = data.apply(lambda row: numpy.mean([row.t0, row.t1, row.t2]), axis=1)
        data["std_dev_temperature"] = data.apply(lambda row: numpy.std([row.t0, row.t1, row.t2]), axis=1)
        zero_kelvin = 273.15
        data["avg_temp_kelvin"] = data["average_temperature"] + zero_kelvin
        air_mass = 0.04 # Kg
        air_heat_capacity = 700 # (j kg^-1 °K^-1)

        data["potential_energy"] = data["avg_temp_kelvin"] * air_mass * air_heat_capacity
        data["potential_energy"] = data["potential_energy"] - data.iloc[0]["potential_energy"]

        fig, (ax1, ax2, ax3, ax4, ax5, ax6) = plt.subplots(6, 1)

        ax1.plot(data["time"], data["t0"], label="t0")
        ax1.plot(data["time"], data["t1"], label="t1")
        ax1.plot(data["time"], data["t2"], label="t2")
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
