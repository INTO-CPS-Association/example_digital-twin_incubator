from oomodelling import Model
import numpy as np


class NoiseFeedthrough(Model):
    def __init__(self, std_dev=0.5):
        super().__init__()

        self.rng = np.random.default_rng()

        self.mean = self.parameter(0.0)
        self.std_dev = self.parameter(std_dev)

        self.u = self.input(lambda: 0.0)
        self.noise = self.var(lambda: self.rng.normal(loc=self.mean, scale=self.std_dev))
        self.y = self.var(lambda: self.noise() + self.u())

        self.save()