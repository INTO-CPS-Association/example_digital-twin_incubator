import math
from oomodelling import ModelSolver
from incubator.models.plant_models.four_parameters_model.four_parameter_model import FourParameterIncubatorPlant
from incubator.models.plant_models.model_functions import create_lookup_table
import numpy as np


class PlantSimulator4Params:
    @staticmethod
    def run_simulation(timespan_seconds, initial_box_temperature, initial_heat_temperature,
                       room_temperature, heater_on,
                       C_air, G_box, C_heater, G_heater):
        timetable = np.array(timespan_seconds)

        room_temperature_fun = create_lookup_table(timetable, np.array(room_temperature))
        # room_temperature_fun = interpolate.interp1d(timetable, np.array(room_temperature))
        heater_on_fun = create_lookup_table(timetable, np.array(heater_on))
        # heater_on_fun = interpolate.interp1d(timetable, np.array(heater_on))

        model = FourParameterIncubatorPlant(initial_room_temperature=room_temperature[0],
                                            initial_box_temperature=initial_box_temperature,
                                            initial_heat_temperature=initial_heat_temperature,
                                            C_air=C_air, G_box=G_box,
                                            C_heater=C_heater, G_heater=G_heater)
        model.in_room_temperature = lambda: room_temperature_fun(model.time())
        model.in_heater_on = lambda: heater_on_fun(model.time())

        start_t = timespan_seconds[0]
        end_t = timespan_seconds[-1]

        controller_step_size = timespan_seconds[1] - timespan_seconds[0]
        # We assume the timeseries is mostly uniform
        for i in range(1, len(timespan_seconds)):
            assert math.fabs(
                controller_step_size - (timespan_seconds[i] - timespan_seconds[i - 1])) <= controller_step_size / 10.0

        sol = ModelSolver().simulate(model, start_t, end_t + controller_step_size,
                                     controller_step_size, controller_step_size / 10.0,
                                     t_eval=timespan_seconds)
        return sol, model
