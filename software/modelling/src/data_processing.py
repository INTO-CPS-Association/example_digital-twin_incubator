import numpy
import pandas
from scipy import integrate

from globals import HEATER_VOLTAGE, HEATER_CURRENT


def load_data(filepath):
    csv = pandas.read_csv(filepath)
    # normalize time
    csv["time"] = csv["time"] - csv.iloc[0]["time"]
    return csv

def derive_data(data):
    data["power_in"] = data.apply(lambda row: HEATER_VOLTAGE * HEATER_CURRENT if row.heater_on else 0.0, axis=1)

    data["energy_in"] = data.apply(
        lambda row: integrate.trapz(data[0:row.name + 1]["power_in"], x=data[0:row.name + 1]["time"]), axis=1)
    data["average_temperature"] = data.apply(lambda row: numpy.mean([row.t2, row.t3]), axis=1)
    zero_kelvin = 273.15
    data["avg_temp_kelvin"] = data["average_temperature"] + zero_kelvin
    air_mass = 0.04  # Kg
    air_heat_capacity = 700  # (j kg^-1 °K^-1)

    data["potential_energy"] = data["avg_temp_kelvin"] * air_mass * air_heat_capacity
    data["potential_energy"] = data["potential_energy"] - data.iloc[0]["potential_energy"]

    return data