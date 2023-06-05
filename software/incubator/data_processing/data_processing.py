import math

import numpy
import pandas
from scipy import integrate

from incubator.communication.shared.protocol import from_ns_to_s
from incubator.config.config import resource_file_path


def load_timestamped_data(filepath, desired_timeframe, time_unit, normalize_time, convert_to_seconds):
    realpath = resource_file_path(filepath)
    csv = pandas.read_csv(realpath)

    start_idx = 0
    while start_idx < len(csv) and csv.iloc[start_idx]["time"] < desired_timeframe[0]:
        start_idx = start_idx + 1

    end_idx = len(csv["time"]) - 1
    while end_idx > 0 and csv.iloc[end_idx]["time"] > desired_timeframe[1]:
        end_idx = end_idx - 1

    if end_idx < start_idx:
        print(
            f"Warning: after trimming data from {filepath}, ended up with start_idx={start_idx} and end_idx={end_idx}. This results in empty data")
        return None

    indices = range(start_idx, end_idx + 1)
    csv = csv.iloc[indices]

    csv["timestamp_ns"] = pandas.to_datetime(csv["time"], unit=time_unit)
    # normalize time
    if normalize_time:
        csv["time"] = csv["time"] - csv.iloc[0]["time"]
    # Convert time
    if convert_to_seconds and time_unit != 's':
        assert time_unit == 'ns', "Other time units not supported."
        csv["time"] = convert_time_s_to_ns(csv["time"])

    return csv


def load_data(filepath,
              events=None,
              desired_timeframe=(- math.inf, math.inf),
              time_unit='s',
              normalize_time=True,
              convert_to_seconds=False):
    data = load_timestamped_data(filepath, desired_timeframe, time_unit, normalize_time, convert_to_seconds)
    event_data = None
    if events is not None:
        assert not normalize_time, "Not allowed to normalize data with events."
        event_data = load_timestamped_data(events, desired_timeframe, time_unit, normalize_time, convert_to_seconds)

    return data, event_data


def convert_time_s_to_ns(timeseries):
    return timeseries.map(lambda time_ns: from_ns_to_s(time_ns))


def convert_event_to_signal(time, events, categories, start):
    """
    Takes event data, that looks like this:
        time,event,code
        1614861060000000000,"Lid Opened", "lid_open"
        1614861220000000000,"Lid Closed", "lid_close"
    And produces a piecewise constant signal, where the values are given by the categories map.
    """
    last_value = categories[start]
    event_idx = 0
    signal = []
    for t in time:
        if event_idx < len(events) and t >= events.iloc[event_idx]["time"]:
            last_value = categories[events.iloc[event_idx]["code"]]
            event_idx += 1
        signal.append(last_value)

    assert len(signal) == len(time)

    return signal


def derive_data(data, V_heater, I_Heater, avg_function=None, events=None):
    if "average_temperature" not in data.columns:
        if avg_function is None:
            raise ValueError("A function to calculate the average temperature is needed but none was provided.")
        data["average_temperature"] = data.apply(avg_function, axis=1)
    data["power_in"] = data.apply(lambda row: V_heater * I_Heater if row.heater_on else 0.0, axis=1)

    data["energy_in"] = data.apply(
        lambda row: integrate.trapz(data[0:row.name + 1]["power_in"], x=data[0:row.name + 1]["time"]), axis=1)
    zero_kelvin = 273.15
    data["avg_temp_kelvin"] = data["average_temperature"] + zero_kelvin
    air_mass = 0.04  # Kg
    air_heat_capacity = 700  # (j kg^-1 °K^-1)

    data["potential_energy"] = data["avg_temp_kelvin"] * air_mass * air_heat_capacity
    data["potential_energy"] = data["potential_energy"] - data.iloc[0]["potential_energy"]

    if events is not None:
        lid_events = events.loc[(events["code"] == "lid_close") | (events["code"] == "lid_open")]
        data["lid_open"] = convert_event_to_signal(data["time"], lid_events,
                                                   categories={"lid_close": 0.0, "lid_open": 1.0},
                                                   start="lid_close")
    else:
        data["lid_open"] = 0.0

    return data
