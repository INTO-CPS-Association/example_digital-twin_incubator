import unittest

from oomodelling import ModelSolver

from controller_model import ControllerModel
import matplotlib.pyplot as plt

from system_model import SystemModel


class CosimulationTests(unittest.TestCase):

    def test_run_cosim_2param_model(self):
        m = SystemModel()

        ModelSolver().simulate(m, 0.0, 10, 0.01)

        plt.figure()
        plt.plot(m.signals['time'], m.plant.signals['T'])

        plt.figure()
        plt.step(m.signals['time'], m.ctrl.signals['heater_on'])

        plt.show()
