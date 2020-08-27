import unittest

import numpy
import scipy
from oomodelling.ModelSolver import ModelSolver
from scipy.optimize import minimize

from src.functions import error, get_experiments, run_experiment
import matplotlib.pyplot as plt

from src.first_principles_model import IncubatorPlant, ComplexIncubatorPlant


class MyTestCase(unittest.TestCase):
    def test_calibrate(self):
        params = [60,  # TON
                  28,  # TOFF
                  0.05,  # heatingG
                  1.0,  # airC
                  0.0005,  # boxG
                  1e3]  # roomC
        params = [6.44278926e+01, 4.84602587e+01, 6.89019487e-01, 6.03816268e+00,
       2.86205065e+00, 1.03504504e+03]
        print(minimize(error, params, method='BFGS', options={'maxiter': 1}))

    def test_plot_experiments(self):
        params = [87,  # TON
                  29,  # TOFF
                  0.032,  # heatingG
                  1.0,  # airC
                  0.00001,  # boxG
                  1e3]  # roomC
        params = [6.44278926e+01, 4.84602587e+01, 6.89019487e-01, 6.03816268e+00,
                  2.86205065e+00, 1.03504504e+03]
        tON = params[0]
        tOFF = params[1]
        experiments = get_experiments(tON, tOFF)
        for i in range(len(experiments)):
            exp = experiments[i]
            m = run_experiment(exp, params, use_teval=False)
            plt.figure()
            plt.title(f"Experiment {i}")
            plt.plot(m.signals['time'], [exp['T0'] for t in m.signals['time']], label="T0")
            plt.plot(m.signals['time'], [exp['TF'] for t in m.signals['time']], label="TF")
            plt.plot(m.signals['time'], m.box_air.signals['T'], label="T")
            plt.plot(m.signals['time'], m.room_air.signals['T'], label="room_air T")
            plt.legend()
        plt.show()

    def test_example_simulation(self):
        def F(t, x):
            return [-x[0]]
        res = scipy.integrate.solve_ivp(F, (0, 10.0), [10.0])
        plt.figure()
        plt.plot(res.t, res.y[0, :], label="x")
        plt.legend()
        plt.show()

    def test_do_prediction(self):
        params = [6.44278926e+01, 4.84602587e+01, 6.89019487e-01, 6.03816268e+00,
                  2.86205065e+00, 1.03504504e+03]
        tON = params[0]
        tOFF = params[1]
        heatingG = params[2]
        airC = params[3]
        boxG = params[4]
        roomC = params[5]
        m = ComplexIncubatorPlant(tOFF, heatingG, airC, boxG, roomC)
        m.box_air.T = 28.8
        ModelSolver().simulate(m, 0.0, 4.0, 0.1)
        plt.figure()
        plt.plot(m.signals['time'], [28 for t in m.signals['time']], label="minT")
        plt.plot(m.signals['time'], [33 for t in m.signals['time']], label="maxT")
        plt.plot(m.signals['time'], m.box_air.signals['T'], label="T")
        plt.legend()
        plt.show()

    def test_do_prediction(self):
        m = IncubatorPlant(heatPow=100, roomT=0, airC=1, boxG=1.0)
        m.box_air.T = 28.8
        ModelSolver().simulate(m, 0.0, 10.0, 0.1)
        plt.figure()
        plt.plot(m.signals['time'], m.box_air.signals['T'], label="T")
        plt.legend()
        plt.show()


if __name__ == '__main__':
    unittest.main()
