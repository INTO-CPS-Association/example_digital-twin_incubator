import unittest

from oomodelling import ModelSolver

import matplotlib.pyplot as plt

from incubator.models.physical_twin_models.system_model import SystemModel
from incubator.tests.cli_mode_test import CLIModeTest


class CosimulationTests(CLIModeTest):

    def test_run_cosim_2param_model(self):
        m = SystemModel(
            initial_heat_voltage=12.0, initial_heat_current=10.0,
            initial_room_temperature=21.0, initial_box_temperature=21.0,
            C_air=1.0, G_box=1.0)

        m.ctrl.T_desired = 38.
        m.ctrl.lower_bound = 10.
        m.ctrl.heating_time = 1.
        m.ctrl.heating_gap = 10.
        m.plant.C_air = 300.

        ModelSolver().simulate(m, 0.0, 1000, comm_step=3.0, max_solver_step=0.1)

        plt.figure()
        plt.plot(m.signals['time'], m.plant.signals['T'])

        plt.figure()
        plt.step(m.signals['time'], m.ctrl.signals['heater_on'])

        plt.figure()
        plt.step(m.signals['time'], m.ctrl.signals['curr_state_model'])

        if self.ide_mode():
            print(m.ctrl.signals['curr_state_model'])
            plt.show()


if __name__ == '__main__':
    unittest.main()
