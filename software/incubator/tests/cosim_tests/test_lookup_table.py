import unittest

from models.plant_models.model_functions import create_lookup_table
from tests.cli_mode_test import CLIModeTest
import numpy as np


class LookupTableTests(CLIModeTest):

    def test_lookup_table(self):
        timerange = np.array([1.0, 2.0, 3.0, 4.0])
        data = timerange
        signal = create_lookup_table(timerange, data)
        self.assertAlmostEqual(signal(1.0), 1.0)
        self.assertAlmostEqual(signal(4.0), 4.0)


if __name__ == '__main__':
    unittest.main()
