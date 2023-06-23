import logging

import numpy as np
from scipy.optimize import minimize

from incubator.interfaces.database import IDatabase
from incubator.simulators.PlantSimulator4Params import PlantSimulator4Params


def compute_error(tracked_solutions, new_state_trajectories):
    assert len(tracked_solutions) == len(
        new_state_trajectories), "Solutions and state trajectories appear inconsistent."
    return np.sum(np.sum(np.power(tracked_solutions - new_state_trajectories, 2)))


class Calibrator:
    def __init__(self, database: IDatabase, plant_simulator: PlantSimulator4Params, conv_xatol, conv_fatol,
                 max_iterations):
        self._l = logging.getLogger("Calibrator")
        self.database = database
        self.plant_simulator = plant_simulator
        self.conv_xatol = conv_xatol
        self.conv_fatol = conv_fatol
        self.max_iterations = max_iterations

    def calibrate(self, t_start, t_end):
        self._l.debug(f"Starting calibration between in times [{t_start}, {t_end}]")
        signals, t_start_idx, t_end_idx = self.database.get_plant_signals_between(t_start, t_end)
        times = signals["time"][t_start_idx:t_end_idx]
        reference_T = signals["T"][t_start_idx:t_end_idx]
        ctrl_signal = signals["in_heater_on"][t_start_idx:t_end_idx]
        reference_T_heater = signals["T_heater"][t_start_idx:t_end_idx]
        room_T = signals["in_room_temperature"][t_start_idx:t_end_idx]
        assert len(reference_T) == len(times) == len(ctrl_signal) == len(reference_T_heater)

        tracked_solutions = np.array([reference_T, reference_T_heater])

        C_air, G_box, C_heater, G_heater, V_heater, I_heater = self.database.get_plant4_parameters()

        def cost(p):
            C_air, G_box = p
            try:
                sol, model = self.plant_simulator.run_simulation(times, reference_T[0], reference_T_heater[0], room_T,
                                                                 ctrl_signal,
                                                                 C_air, G_box, C_heater, G_heater, V_heater, I_heater)

                error = compute_error(tracked_solutions, sol.y[1:])
                return error
            except ValueError as e:
                print("Simulation failed with the following parameters and initial conditions:")
                print(f"C_air={C_air}, G_box={G_box}, C_heater={C_heater}, G_heater={G_heater}, "
                      f"={V_heater}, I_heater={I_heater}")
                print(f"T0={reference_T[0]}, T_heater0={reference_T_heater[0]}")
                raise e

        new_sol = minimize(cost, np.array([C_air, G_box]), method='Nelder-Mead', bounds=[(150.0, 1e4), (0.1, 1e4)],
                           options={'xatol': self.conv_xatol, 'fatol': self.conv_fatol, 'maxiter': self.max_iterations})

        assert new_sol.success, new_sol.message

        if new_sol.success:
            C_air_new, G_box_new = new_sol.x
            calibrated_sol, _ = self.plant_simulator.run_simulation(times, reference_T[0], reference_T_heater[0],
                                                                    room_T, ctrl_signal,
                                                                    C_air_new, G_box_new, C_heater, G_heater,
                                                                    V_heater, I_heater)

            self.database.store_calibrated_trajectory(times, calibrated_sol.y[1:])
            self.database.store_new_plant_parameters(times[0], C_air_new, G_box_new, C_heater, G_heater, V_heater, I_heater)
            return True, C_air_new, G_box_new, C_heater, G_heater, V_heater, I_heater
        else:
            return False, C_air, G_box, C_heater, G_heater, V_heater, I_heater
