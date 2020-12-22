import math

import numpy
import pandas
from scipy import integrate

from digital_twin.fsutils import resource_file_path
from digital_twin.models.plant_models.globals import HEATER_VOLTAGE, HEATER_CURRENT


def load_data(filepath, desired_timeframe=(- math.inf, math.inf)):
    realpath = resource_file_path(filepath)
    csv = pandas.read_csv(realpath)
    csv["timestamp"] = pandas.to_datetime(csv["time"], unit='s')
    # normalize time
    csv["time"] = csv["time"] - csv.iloc[0]["time"]

    start_idx = 0
    while csv.iloc[start_idx]["time"] < desired_timeframe[0]:
        start_idx = start_idx + 1

    end_idx = len(csv["time"]) - 1
    while csv.iloc[end_idx]["time"] > desired_timeframe[1]:
        end_idx = end_idx - 1

    assert start_idx < end_idx

    indices = range(start_idx, end_idx + 1)
    csv = csv.iloc[indices]

    return derive_data(csv)


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

