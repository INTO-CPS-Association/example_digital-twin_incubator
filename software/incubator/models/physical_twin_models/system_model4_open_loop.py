from oomodelling import Model, ModelSolver

from incubator.models.controller_models.controller_open_loop import ControllerOpenLoop
from incubator.models.plant_models.four_parameters_model.four_parameter_model import FourParameterIncubatorPlant


class SystemModel4ParametersOpenLoopSimulator:
    @staticmethod
    def run_simulation(t0, tf,
                       # Initial state
                       initial_T, initial_T_heater, initial_room_T,
                       # Controller parameters
                       n_samples_heating: int, n_samples_period: int, controller_step_size: float,
                       # Plant parameters
                       C_air, G_box, C_heater, G_heater, V_heater, I_heater):
        model = SystemModel4ParametersOpenLoop(n_samples_period, n_samples_heating,
                                               C_air, G_box, C_heater, G_heater, V_heater, I_heater,
                                               initial_box_temperature=initial_T,
                                               initial_heat_temperature=initial_T_heater,
                                               initial_room_temperature=initial_room_T)

        # Wire the lookup table to the _plant
        model.plant.in_room_temperature = lambda: initial_room_T

        # Run simulation
        sol = ModelSolver().simulate(model, t0, tf,
                                     controller_step_size,
                                     controller_step_size / 10.0)

        # Return model that has the results
        return model


class SystemModel4ParametersOpenLoop(Model):
    def __init__(self,
                 # Controller parameters
                 n_samples_period, n_samples_heating,
                 # Plant parameters
                 C_air,
                 G_box,
                 C_heater,
                 G_heater,
                 V_heater, I_heater,
                 initial_box_temperature,
                 initial_heat_temperature,
                 initial_room_temperature):
        super().__init__()

        self.ctrl = ControllerOpenLoop(n_samples_period, n_samples_heating)
        self.plant = FourParameterIncubatorPlant(
            initial_heat_voltage=V_heater,
            initial_heat_current=I_heater,
            initial_room_temperature=initial_room_temperature,
            initial_box_temperature=initial_box_temperature,
            initial_heat_temperature=initial_heat_temperature,
            C_air=C_air,
            G_box=G_box,
            C_heater=C_heater,
            G_heater=G_heater)

        self.plant.in_heater_on = self.ctrl.heater_on

        self.save()
