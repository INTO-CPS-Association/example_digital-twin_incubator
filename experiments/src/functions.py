from oomodelling.ModelSolver import ModelSolver

from src.data import get_experiments
from src.first_principles_model import IncubatorPlant

def run_experiment(exp, params, use_teval=True):
    heatingG = params[2]
    airC = params[3]
    boxG = params[4]
    roomC = params[5]
    m = IncubatorPlant(exp["Tin"], heatingG, airC, boxG, roomC)
    m.air.T = exp["T0"]
    t_eval = (0.0, exp["time_f"]) if use_teval else None
    ModelSolver().simulate(m, 0.0, exp["time_f"], 0.1, t_eval)
    return m


def error(params):
    tON = params[0]
    tOFF = params[1]
    experiments = get_experiments(tON, tOFF)

    errors = []
    for exp in experiments:
        m = run_experiment(exp, params)
        est_TF = m.air.signals['T'][-1]
        errors.append((exp["TF"] - est_TF) ** 2)

    cost = sum(errors)
    return cost
