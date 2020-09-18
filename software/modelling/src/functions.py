import numpy
from oomodelling.ModelSolver import ModelSolver

from data_processing import derive_data, load_data
from two_parameter_model import TwoParameterIncubatorPlant

import logging

l = logging.getLogger("Functions")

def find_closest_idx(t, start_idx, time_range):
    assert start_idx >= 0
    idx = start_idx

    maxIdx = len(time_range)

    # Search backward
    while time_range[idx] > t:
        idx = idx - 1

    assert idx >= 0
    assert time_range[idx] <= t, f"{t}, {start_idx}, {idx}"

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
    last_idx = 0

    def signal(t):
        nonlocal last_idx  # See http://zetcode.com/python/python-closures/
        last_idx = find_closest_idx(t, last_idx, time_range)
        return data[last_idx]  # constant extrapolation

    return signal


def run_experiment(data, params, h=3.0):
    C_air = params[0]
    G_box = params[1]

    model = TwoParameterIncubatorPlant(initial_room_temperature=data.iloc[0]["t1"],
                                       initial_box_temperature=data.iloc[0]["average_temperature"],
                                       C_air=C_air, G_box=G_box)

    in_heater_table = create_lookup_table(data["time"], data["heater_on"])
    in_room_temperature = create_lookup_table(data["time"], data["t1"])
    model.in_heater_on = lambda: in_heater_table(model.time())
    model.in_room_temperature = lambda: in_room_temperature(model.time())
    model.C_air = C_air
    model.G_box = G_box

    tf = data.iloc[-1]["time"]
    sol = ModelSolver().simulate(model, 0.0, tf, h, t_eval=data["time"])
    return model, sol


def construct_residual(experiments):
    def residual(params):
        errors = []
        for exp in experiments:
            data = derive_data(load_data(exp))
            m, sol = run_experiment(data, params, h=3.0)
            state_names = m.state_names()
            state_over_time = sol.y

            T_indexes = numpy.where(state_names == 'T')
            assert len(T_indexes) == 1
            approx_Troom = state_over_time[T_indexes[0], :][0]
            Troom = data["average_temperature"].to_numpy()
            assert len(approx_Troom) == len(Troom), f"Inconsistent troom arrays. One has {len(approx_Troom)} elements " \
                                                    f"and the other one has {len(Troom)}. " \
                                                    f"Their shapes are {approx_Troom.shape} and {Troom.shape}"
            assert approx_Troom.shape == Troom.shape, f"Inconsistent troom arrays. One has shape {approx_Troom.shape} elements " \
                                                    f"and the other one has {Troom.shape}."
            res = Troom - approx_Troom
            cost = sum(res**2)
            l.info(f"Parameters {params} -> Cost: {cost}")
            return res

        cost = sum(errors)
        return cost
    return residual