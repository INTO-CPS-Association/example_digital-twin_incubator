from incubator.models.plant_models.two_parameters_model.two_parameter_model import TwoParameterIncubatorPlant


class FourParameterIncubatorPlant(TwoParameterIncubatorPlant):
    """
    NOTE: This model inherits from the two parameter model so that we can reuse some of the equations
    but the parameters, while having the same name, do not have the same meaning.
    For example the C_air parameter has a very different meaning in this model
    when compared to the C_air parameter in the two parameter model.
    This is because the two parameter model is actually lumping the heater, air, and box, into the same entity,
    whereas the four parameter model is just lumping the air and box, and contains a separate variable for the heater.
    """
    def __init__(self,
                 initial_heat_voltage, initial_heat_current,
                 initial_room_temperature, initial_box_temperature,
                 initial_heat_temperature,
                 C_air, G_box,
                 C_heater, G_heater):
        # Initialize 2p stuff.
        super(FourParameterIncubatorPlant, self).__init__(initial_heat_voltage, initial_heat_current,
                                                          initial_room_temperature, initial_box_temperature, C_air,
                                                          G_box)

        self.edit()  # Go into edit mode

        self.C_heater = self.parameter(C_heater)
        self.G_heater = self.parameter(G_heater)

        self.T_heater = self.state(initial_heat_temperature)

        self.power_transfer_heat = self.var(lambda: self.G_heater * (self.T_heater() - self.T()))

        self.total_power_heater = self.var(lambda: self.power_in() - self.power_transfer_heat())

        # Override equation of TwoParameterIncubatorPlant
        self.total_power_box = self.ovar(lambda: self.power_transfer_heat() - self.power_out_box())

        self.der('T_heater', lambda: (1.0 / self.C_heater) * (self.total_power_heater()))

        self.save()  # Close edit mode
