class IUpdateableKalmanFilter:
    def update_parameters(self, C_air, G_box, C_heater, G_heater, V_heater, I_heater):
        raise NotImplementedError("To be implemented by subclasses")
