import unittest

from oomodelling import ModelSolver

import matplotlib.pyplot as plt

from incubator.models.physical_twin_models.system_model import SystemModel
from incubator.tests.cli_mode_test import CLIModeTest


class CosimulationTests(CLIModeTest):

    def test_run_cosim_2param_model(self):
        m = SystemModel()

        ModelSolver().simulate(m, 0.0, 10, 0.01, 0.001)

        plt.figure()
        plt.plot(m.signals['time'], m.plant.signals['T'])

        plt.figure()
        plt.step(m.signals['time'], m.ctrl.signals['heater_on'])

        if self.ide_mode():
            plt.show()


if __name__ == '__main__':
    unittest.main()
