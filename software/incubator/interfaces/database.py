class IDatabase:

    def get_plant_signals_between(self, t_start_s, t_end_s):
        raise NotImplementedError("For subclasses")

    def store_calibrated_trajectory(self, times, calibrated_sol):
        raise NotImplementedError("For subclasses")

    def store_new_plant_parameters(self, start_time_s, C_air_new, G_box_new, C_heater, G_heater, V_heater, I_heater):
        raise NotImplementedError("For subclasses")

    def get_plant4_parameters(self):
        raise NotImplementedError("For subclasses")

    def get_plant_snapshot(self):
        raise NotImplementedError("For subclasses")

    def get_ctrl_parameters(self):
        raise NotImplementedError("For subclasses")

    def store_new_ctrl_parameters(self, start_time_s, n_samples_heating_new, n_samples_period_new, controller_step_size):
        raise NotImplementedError("For subclasses")

    def store_controller_optimal_policy(self, times, T, T_heater, heater_on):
        raise NotImplementedError("For subclasses")
