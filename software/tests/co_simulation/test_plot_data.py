import math
import unittest

import matplotlib.pyplot as plt

from digital_twin.data_processing.data_processing import load_data
from digital_twin.visualization.data_plotting import plot_incubator_data
from tests.cli_mode_test import CLIModeTest


class TestsModelling(CLIModeTest):

    def test_plot_data_default_setup(self):
        # CWD: Example_Digital-Twin_Incubator\software\
        data = load_data("../datasets/calibration_fan_24v/semi_random_movement.csv",
                         desired_timeframe=(- math.inf, 2000))

        plot_incubator_data(data)

        if self.ide_mode():
            plt.show()


if __name__ == '__main__':
    unittest.main()
