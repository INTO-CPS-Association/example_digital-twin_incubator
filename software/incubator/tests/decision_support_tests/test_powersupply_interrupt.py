import unittest

import matplotlib.pyplot as plt
from oomodelling import ModelSolver

from incubator.models.physical_twin_models.system_model4 import SystemModel4Parameters
from incubator.models.plant_models.four_parameters_model.best_parameters import four_param_model_params
from incubator.physical_twin.low_level_driver_server import CTRL_EXEC_INTERVAL
from incubator.tests.cli_mode_test import CLIModeTest


class CosimulationTests(CLIModeTest):

    def test_run_cosim_4param_model(self):
        powerfull_sys_parameters = [
            177.62927865,  # C_air
            0.77307655,  # G_box
            239.61236331,  # C_heater
            2.31872819,  # G_heater
            12.16,  # V_heater
            1.54,  # I_heater
        ]

        C_air = powerfull_sys_parameters[0]
        G_box = powerfull_sys_parameters[1]
        C_heater = powerfull_sys_parameters[2]
        G_heater = powerfull_sys_parameters[3]
        V_heater = powerfull_sys_parameters[4]
        I_heater = powerfull_sys_parameters[5]

        fig = plt.figure()

        def show_trace(heating_time):
            m = SystemModel4Parameters(C_air,
                                       G_box,
                                       C_heater,
                                       G_heater,
                                       V_heater, I_heater,
                                       lower_bound=20, heating_time=heating_time, heating_gap=20000.0,
                                       max_temperature_desired=50, initial_box_temperature=35,
                                       initial_heat_temperature=35,
                                       initial_room_temperature=22)
            ModelSolver().simulate(m, 0.0, 2000, CTRL_EXEC_INTERVAL, CTRL_EXEC_INTERVAL / 10.0)

            plt.plot(m.signals['time'], m.plant.signals['T'], label=f"Trial_{heating_time}")
            plt.plot(m.signals['time'], [50 if h else 20 for h in m.ctrl.signals['heater_on']], label=f"Trial_{heating_time}")

        # show_trace(0.1)
        # show_trace(1.0)
        # show_trace(3.0)
        # show_trace(100.0)
        # show_trace(200.0)
        show_trace(300.0)
        show_trace(400.0)
        show_trace(500.0)

        plt.legend()

        if self.ide_mode():
            plt.show()
        plt.close(fig)

if __name__ == '__main__':
    unittest.main()
