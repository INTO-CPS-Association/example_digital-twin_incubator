import math
import os
import tempfile
import unittest

import matplotlib.pyplot as plt
from digital_twin.data_processing.data_processing import load_data
from digital_twin.visualization.data_plotting import plot_incubator_data, plotly_incubator_data, show_plotly
from tests.cli_mode_test import CLIModeTest


class TestPlotData(CLIModeTest):

    def test_plot_data_default_setup(self):
        # CWD: Example_Digital-Twin_Incubator\software\
        data = load_data("../datasets/calibration_fan_24v/semi_random_movement.csv",
                         desired_timeframe=(- math.inf, 2000))

        plot_incubator_data(data)

        if self.ide_mode():
            plt.show()

    def test_plot_data_plotly(self):
        data = load_data("../datasets/calibration_fan_24v/semi_random_movement.csv",
                         desired_timeframe=(- math.inf, 2000))

        fig = plotly_incubator_data(data)

        if self.ide_mode():
            show_plotly(fig)



if __name__ == '__main__':
    unittest.main()
