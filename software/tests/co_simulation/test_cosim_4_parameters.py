import unittest

from oomodelling import ModelSolver

import matplotlib.pyplot as plt

from digital_twin.models.plant_models.four_parameters_model.system_model4 import SystemModel4Parameters
from tests.cli_mode_test import CLIModeTest


class CosimulationTests(CLIModeTest):

    def test_run_cosim_4param_model(self):
        params = [486.1198196,  # C_air
                  0.85804919,  # G_box
                  33.65074598,  # C_heater
                  0.86572258]  # G_heater
        C_air_num = params[0]
        G_box_num = params[1]
        C_heater_num = params[2]
        G_heater_num = params[3]

        plt.figure()

        def show_trace(heating_time):
            m = SystemModel4Parameters(C_air=C_air_num,
                                  G_box=G_box_num,
                                  C_heater=C_heater_num,
                                  G_heater=G_heater_num, heating_time=heating_time, heating_gap=2.0)
            ModelSolver().simulate(m, 0.0, 1200, 0.5)

            plt.plot(m.signals['time'], m.plant.signals['T'], label=f"Trial_{heating_time}")

        show_trace(0.1)
        show_trace(1.0)
        show_trace(10.0)
        show_trace(100.0)

        plt.legend()

        if self.ide_mode():
            plt.show()


if __name__ == '__main__':
    unittest.main()
