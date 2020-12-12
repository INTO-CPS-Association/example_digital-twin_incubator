import math
import unittest

from filterpy.common import Q_discrete_white_noise
from filterpy.kalman import KalmanFilter
from scipy import linalg

from tests.cli_mode_test import CLIModeTest
import numpy as np
import matplotlib.pyplot as plt


class TestKalmanFilter(CLIModeTest):

    def test_dummy_kalman(self):

        # Linear system equation
        dt = 0.1
        A = np.array([[1., dt],
                      [0., 1.]])  # Spring equation

        std_dev = 0.001

        f = KalmanFilter(dim_x=2, dim_z=1, dim_u=1)
        f.x = np.array([[0.],  # position
                        [0.]])  # velocity
        f.F = A
        f.B = np.array([[0.],  # position
                        [dt]])  # velocity
        f.H = np.array([[1., 0.]])  # We only measure position
        f.P = np.array([[100., 0.],
                        [0., 100.]])
        f.R = np.array([[std_dev]])
        f.Q = Q_discrete_white_noise(dim=2, dt=dt, var=std_dev**2)

        time = np.arange(0, 10, dt)
        Nsamples = len(time)
        gaussian_noise = np.random.normal(scale=std_dev, size=Nsamples)
        acceleration = np.array([0.1 for t in time])
        velocity = np.array([a*t for (t,a) in zip(time, acceleration)])
        position = np.array([v*t + 0.5*a*(t**2) for (t,a,v) in zip(time, acceleration, velocity)])
        model_noise = position + gaussian_noise

        kalman_prediction = []
        for (z, u) in zip(model_noise, acceleration):
            f.predict(u=np.array([[u]]))
            f.update(np.array([[z]]))
            kalman_prediction.append(f.x)

        kalman_prediction = np.array(kalman_prediction).squeeze(2)
        assert kalman_prediction.shape == (Nsamples, 2)

        plt.figure()
        plt.plot(time, model_noise)
        # plt.plot(time, gaussian_noise)
        plt.plot(time, kalman_prediction[:, 0], label="~position")
        plt.plot(time, kalman_prediction[:, 1], label="~velocity")
        plt.plot(time, velocity, label="velocity")

        plt.legend()

        if self.ide_mode():
            plt.show()










if __name__ == '__main__':
    unittest.main()
