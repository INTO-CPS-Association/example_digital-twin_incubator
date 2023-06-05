import math
import unittest

import numpy as np
import pandas
from matplotlib import pyplot as plt

from incubator.config.config import resource_file_path
from incubator.data_processing.data_processing import load_timestamped_data
from incubator.tests.cli_mode_test import CLIModeTest


class TestCurrentMeasurements(CLIModeTest):

    def test_plot_current_measurements(self):
        csv = load_timestamped_data("incubator/datasets/20230605_measure_voltage_current/currents.csv",
                                    desired_timeframe=(-math.inf, math.inf),
                                    time_unit='ns',
                                    normalize_time=False,
                                    convert_to_seconds=False)

        plt.figure()

        plt.plot(csv["timestamp_ns"], csv["current"], label="I(A)")
        plt.plot(csv["timestamp_ns"], [np.average(csv["current"]) for _ in csv["timestamp_ns"]], label="Average")
        plt.legend()

        if self.ide_mode():
            print(f'Average is {np.round(np.average(csv["current"]), 2)} A')
            plt.show()


if __name__ == '__main__':
    unittest.main()
