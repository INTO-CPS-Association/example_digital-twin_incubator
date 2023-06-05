import math

import numpy
import numpy as np
from oomodelling.ModelSolver import ModelSolver

import logging

from incubator.models.plant_models.four_parameters_model.four_parameter_model import FourParameterIncubatorPlant
from incubator.models.plant_models.seven_parameters_model.seven_parameter_model import SevenParameterIncubatorPlant
from incubator.models.plant_models.two_parameters_model.two_parameter_model import TwoParameterIncubatorPlant
from incubator.physical_twin.low_level_driver_server import CTRL_EXEC_INTERVAL

l = logging.getLogger("Functions")


def find_closest_idx(t, start_idx, time_range):
    assert start_idx >= 0
    idx = start_idx

    maxIdx = len(time_range)

    # Search backward
    while time_range[idx] > t and idx > 0:
        idx = idx - 1

    assert time_range[idx] <= t, f"{t}, {start_idx}, {idx}, {time_range[idx]}, {time_range[-1]}"

    # Search forward
    while (idx + 1) < maxIdx and time_range[idx + 1] <= t:
        idx = idx + 1

    assert idx < maxIdx
    assert time_range[idx] <= t < (time_range[idx + 1] if (idx + 1 < maxIdx) else math.inf)

    return idx


def create_lookup_table(time_range, data):
    """
    Implements an efficient lookup table.
    Uses the last_idx as a memory of the last request.
    Assumes that t is mostly increasing.
    """
    assert type(time_range) is np.ndarray, "Recommended to use numpy arrays for performance reasons."
    assert type(data) is np.ndarray, "Recommended to use numpy arrays for performance reasons."

    last_idx = 0

    def signal(t):
        nonlocal last_idx  # See http://zetcode.com/python/python-closures/
        last_idx = find_closest_idx(t, last_idx, time_range)
        return data[last_idx]  # constant extrapolation

    return signal


def run_experiment_two_parameter_model(data, params, h=CTRL_EXEC_INTERVAL):
    C_air = params[0]
    G_box = params[1]
    V_heater = params[2]
    I_heater = params[3]

    model = TwoParameterIncubatorPlant(initial_heat_voltage=V_heater,
                                       initial_heat_current=I_heater,
                                       initial_room_temperature=data.iloc[0]["T_room"],
                                       initial_box_temperature=data.iloc[0]["average_temperature"],
                                       C_air=C_air, G_box=G_box)

    time_range = data["time"].to_numpy()

    in_heater_table = create_lookup_table(time_range, data["heater_on"].to_numpy())
    in_room_temperature = create_lookup_table(time_range, data["T_room"].to_numpy())
    model.in_heater_on = lambda: in_heater_table(model.time())
    model.in_room_temperature = lambda: in_room_temperature(model.time())

    t0 = data.iloc[0]["time"]
    tf = data.iloc[-1]["time"]
    sol = ModelSolver().simulate(model, t0, tf, h, h / 10.0, t_eval=data["time"])
    return model, sol


def run_experiment_four_parameter_model(data, params, h=CTRL_EXEC_INTERVAL):
    C_air = params[0]
    G_box = params[1]
    C_heater = params[2]
    G_heater = params[3]
    V_heater = params[4]
    I_heater = params[5]

    model = FourParameterIncubatorPlant(initial_room_temperature=data.iloc[0]["T_room"],
                                        initial_box_temperature=data.iloc[0]["average_temperature"],
                                        initial_heat_temperature=data.iloc[0]["average_temperature"],
                                        C_air=C_air, G_box=G_box,
                                        C_heater=C_heater, G_heater=G_heater,
                                        initial_heat_voltage=V_heater,
                                        initial_heat_current=I_heater)

    time_range = data["time"].to_numpy()

    in_heater_table = create_lookup_table(time_range, data["heater_on"].to_numpy())
    in_room_temperature = create_lookup_table(time_range, data["T_room"].to_numpy())
    model.in_heater_on = lambda: in_heater_table(model.time())
    model.in_room_temperature = lambda: in_room_temperature(model.time())

    t0 = data.iloc[0]["time"]
    tf = data.iloc[-1]["time"]
    sol = ModelSolver().simulate(model, t0, tf, h, h / 10.0, t_eval=time_range)
    return model, sol


def run_experiment_seven_parameter_model(data, params,
                                         initial_heat_temperature,
                                         h=CTRL_EXEC_INTERVAL):
    C_air = params[0]
    G_box = params[1]
    C_heater = params[2]
    G_heater = params[3]
    C_object = params[4]
    G_object = params[5]
    G_open_lid = params[6]
    V_heater = params[7]
    I_heater = params[8]

    initial_room_temperature = data.iloc[0]["T_room"]
    initial_box_temperature = data.iloc[0]["average_temperature"]

    model = SevenParameterIncubatorPlant(V_heater, I_heater,
                                         initial_room_temperature, initial_box_temperature,
                                         initial_heat_temperature,
                                         C_air, G_box,
                                         C_heater, G_heater,
                                         C_object, G_object,
                                         G_open_lid)

    time_range = data["time"].to_numpy()

    in_heater_table = create_lookup_table(time_range, data["heater_on"].to_numpy())
    in_lid_open = create_lookup_table(time_range, data["lid_open"].to_numpy())
    in_room_temperature = create_lookup_table(time_range, data["t3"].to_numpy())
    model.in_heater_on = lambda: in_heater_table(model.time())
    model.in_room_temperature = lambda: in_room_temperature(model.time())
    model.in_lid_open = lambda: in_lid_open(model.time())

    t0 = data.iloc[0]["time"]
    tf = data.iloc[-1]["time"]
    sol = ModelSolver().simulate(model, t0, tf, h, h / 10.0, t_eval=data["time"])
    return model, sol


def construct_residual(experiments):
    """
    run_exp is, for instance, run_experiment_four_parameter_model
    """

    def residual(params):
        errors = []
        for run_exp in experiments:
            m, sol, data = run_exp(params)
            state_names = m.state_names()
            state_over_time = sol.y

            T_indexes = numpy.where(state_names == 'T')
            assert len(T_indexes) == 1
            approx_T = state_over_time[T_indexes[0], :][0]
            T = data["average_temperature"].to_numpy()
            assert len(approx_T) == len(T), f"Inconsistent temperature arrays. One has {len(approx_T)} elements " \
                                            f"and the other one has {len(T)}. " \
                                            f"Their shapes are {approx_T.shape} and {T.shape}"
            assert approx_T.shape == T.shape, f"Inconsistent temperature arrays. One has shape {approx_T.shape} elements " \
                                              f"and the other one has {T.shape}."
            res = T - approx_T
            cost = sum(res ** 2)
            l.info(f"Parameters {params} -> Cost: {cost}")
            return res

        cost = sum(errors)
        return cost

    return residual
