from oomodelling.ModelSolver import ModelSolver

from first_principles_model import IncubatorPlant


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


def run_experiment(data, params):
    C_air = params[0]
    G_box = params[1]

    model = IncubatorPlant(initial_room_temperature=data.iloc[0]["t1"],
                           initial_box_temperature=data.iloc[0]["t1"],
                           C_air=C_air, G_box=G_box)

    in_heater_table = create_lookup_table(data["time"], data["heater_on"])
    in_room_temperature = create_lookup_table(data["time"], data["t1"])
    model.in_heater_on = lambda: in_heater_table(model.time())
    model.in_room_temperature = lambda: in_room_temperature(model.time())
    model.C_air = C_air
    model.G_box = G_box

    tf = data.iloc[-1]["time"]
    h = 1.0
    ModelSolver().simulate(model, 0.0, tf, h)
    return model


def construct_error(experiments):
    def error(params):
        errors = []
        for exp in experiments:
            m = run_experiment(exp, params)
            est_TF = m.box_air.signals['T'][-1]
            errors.append((exp["TF"] - est_TF) ** 2)

        cost = sum(errors)
        return cost
