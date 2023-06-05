from incubator.models.plant_models.four_parameters_model.four_parameter_model import FourParameterIncubatorPlant


class SevenParameterIncubatorPlant(FourParameterIncubatorPlant):
    def __init__(self,
                 initial_heat_voltage=12.0, initial_heat_current=10.0,
                 initial_room_temperature=21.0, initial_box_temperature=25.0,
                 initial_heat_temperature=25.0,
                 C_air=1.0, G_box=1.0,
                 C_heater=1.0, G_heater=1.0,
                 C_object=1.0, G_object=1.0,
                 G_open_lid=1.0):
        # Initialize 2p stuff
        super().__init__(initial_heat_voltage, initial_heat_current,
                         initial_room_temperature, initial_box_temperature,
                         initial_heat_temperature,
                         C_air, G_box,
                         C_heater, G_heater)

        self.edit()  # Go into edit mode

        self.object_in = self.input(lambda: 0.0)
        self.in_lid_open = self.input(lambda: 0.0)

        self.C_object = self.parameter(C_object)
        self.G_object = self.parameter(G_object)
        self.G_open_lid = self.parameter(G_open_lid)

        # self.T_object = self.state(initial_room_temperature)

        # self.power_transfer_object = self.var(lambda: self.object_in() * self.G_object * (self.T() - self.T_object()))

        # self.der('T_object', lambda: (1.0 / self.C_object) * (self.power_transfer_object()))

        # Override equation of FourParameterIncubatorPlant
        # self.total_power_box = self.ovar(lambda: self.power_transfer_heat() - self.power_transfer_object() - self.power_out_box())

        # Override equation of TwoParameterincubatorPlant
        self.power_out_box = self.ovar(lambda: (((1-self.in_lid_open()) * self.G_box()) + self.in_lid_open() * self.G_open_lid) * (self.T() - self.in_room_temperature()))

        self.save()  # Close edit mode
