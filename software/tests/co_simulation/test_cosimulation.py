import unittest

from oomodelling import ModelSolver

import matplotlib.pyplot as plt

from digital_twin.models.plant_models.two_parameters_model.system_model import SystemModel
from tests.cli_mode_test import CLIModeTest


class CosimulationTests(CLIModeTest):

    def test_run_cosim_2param_model(self):
        m = SystemModel()

        ModelSolver().simulate(m, 0.0, 10, 0.01)

        plt.figure()
        plt.plot(m.signals['time'], m.plant.signals['T'])

        plt.figure()
        plt.step(m.signals['time'], m.ctrl.signals['heater_on'])

        if self.ide_mode():
            plt.show()


if __name__ == '__main__':
    unittest.main()
