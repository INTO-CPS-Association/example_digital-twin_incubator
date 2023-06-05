import numpy as np
from scipy.optimize import minimize_scalar

from incubator.interfaces.parametric_controller import IParametricController
from incubator.interfaces.database import IDatabase
from incubator.models.physical_twin_models.system_model4_open_loop import SystemModel4ParametersOpenLoopSimulator


class IControllerOptimizer:
    def optimize_controller(self):
        raise NotImplementedError("For subclasses")


class ControllerOptimizer(IControllerOptimizer):

    def __init__(self, database: IDatabase,
                 pt_simulator: SystemModel4ParametersOpenLoopSimulator,
                 controller: IParametricController,
                 conv_xatol, conv_fatol, max_iterations, restrict_T_heater,
                 desired_temperature, max_t_heater):
        self.conv_xatol = conv_xatol
        self.conv_fatol = conv_fatol
        self.max_iterations = max_iterations
        self.database = database
        self.pt_simulator = pt_simulator
        self.controller = controller
        self.restrict_T_heater = restrict_T_heater
        self.desired_temperature = desired_temperature
        self.max_t_heater = max_t_heater

    def optimize_controller(self):
        # Get system snapshot
        time_s, T, T_heater, room_T = self.database.get_plant_snapshot()

        # Get system parameters
        C_air, G_box, C_heater, G_heater, V_heater, I_heater = self.database.get_plant4_parameters()

        time_til_steady_state = time_s + 3000  # Obtained from empirical experiments

        # Get current controller parameters
        n_samples_heating, n_samples_period, controller_step_size = self.database.get_ctrl_parameters()

        # Define cost function for controller
        def cost(p):
            n_samples_heating_guess = round(p)

            model = self.pt_simulator.run_simulation(time_s, time_til_steady_state, T, T_heater, room_T,
                                                     n_samples_heating_guess, n_samples_period, controller_step_size,
                                                     C_air, G_box, C_heater, G_heater, V_heater, I_heater)
            # Error is how far from the desired temperature the simulation is, for a few seconds in steady state.
            range_T_for_error = np.array(model.plant.signals['T'][-100:-1])
            error = np.sum(np.power(range_T_for_error - self.desired_temperature, 2))
            if self.restrict_T_heater:
                range_T_heater_for_error = np.array(model.plant.signals['T_heater'][-100:-1])
                saturation_of_max_t_heater = range_T_heater_for_error - self.max_t_heater
                # Replace negative values with zero, so only signals that exceeds max_t_heater remains.
                saturation_of_max_t_heater[saturation_of_max_t_heater < 0] = 0.
                error += np.sum(np.power(saturation_of_max_t_heater, 4))
            return error

        # Start optimization process - The process uses braketing
        # and therefore assumes that
        # cost(n_samples_heating) < cost(max_samples_heating) and cost(n_samples_heating) < cost(0)
        # If that's not true, then it means the best controller configuration is at the extremes.
        # Ensure that the initial guess for n_samples_period is not zero,
        #   in order to avoid getting stuck in the same policy forever.
        n_samples_heating = max(1, n_samples_heating)
        ca = cost(0)
        cb = cost(n_samples_heating)
        cc = cost(n_samples_period)
        if not (cb < ca and cb < cc):
            if ca < cc:
                assert ca <= cb and ca < cc
                n_samples_heating_new = 0
            else:
                assert cc <= cb and cc <= ca
                n_samples_heating_new = n_samples_period
        else:
            new_sol = minimize_scalar(cost, bracket=[0, n_samples_heating, n_samples_period],
                                      method='Brent', tol=self.conv_xatol)

            assert new_sol.success, new_sol.message

            n_samples_heating_new = round(new_sol.x)

        assert n_samples_heating_new is not None
        # Record parameters and update controller
        self.controller.set_new_parameters(n_samples_heating_new, n_samples_period)
        self.database.store_new_ctrl_parameters(time_s, n_samples_heating_new, n_samples_period, controller_step_size)
        # Store predicted simulation, for debugging purposes
        model = self.pt_simulator.run_simulation(time_s, time_til_steady_state, T, T_heater, room_T,
                                                 n_samples_heating_new, n_samples_period, controller_step_size,
                                                 C_air, G_box, C_heater, G_heater, V_heater, I_heater)
        self.database.store_controller_optimal_policy(model.signals['time'],
                                                      model.plant.signals['T'],
                                                      model.plant.signals['T_heater'],
                                                      model.ctrl.signals['heater_on'])


class NoOPControllerOptimizer(IControllerOptimizer):
    def optimize_controller(self):
        pass
