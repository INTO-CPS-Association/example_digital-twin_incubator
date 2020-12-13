import math
import unittest

import numpy as np

from digital_twin.data_processing.data_processing import load_data
from digital_twin.models.plant_models.model_functions import run_experiment_four_parameter_model
from digital_twin.monitoring.kalman_filter_4p import KalmanFilter4P
from digital_twin.visualization.data_plotting import plotly_incubator_data, show_plotly
from tests.cli_mode_test import CLIModeTest


class TestKalmanFilter(CLIModeTest):

    def test_kalman_4_param_model(self):
        data_sample_size = 3.0

        # Load the data
        tf = 2000.0 if self.ide_mode() else 800.0
        data = load_data("../datasets/calibration_fan_24v/semi_random_movement.csv",
                         desired_timeframe=(- math.inf, tf))

        time = data["time"]

        # Inputs to model
        measurements_heater = np.array([1.0 if b else 0.0 for b in data["heater_on"]])
        measurements_Troom = data["t1"].to_numpy()

        # System state
        measurements_T = data["average_temperature"].to_numpy()

        std_dev = 0.00001

        params = [486.1198196,  # C_air
                  0.85804919,  # G_box
                  33.65074598,  # C_heater
                  0.86572258]  # G_heater
        C_air_num = params[0]
        G_box_num = params[1]
        C_heater_num = params[2]
        G_heater_num = params[3]

        f = KalmanFilter4P(data_sample_size, std_dev,
                           C_air=C_air_num,
                           G_box=G_box_num,
                           C_heater=C_heater_num,
                           G_heater=G_heater_num,
                           initial_room_temperature=25.0,
                           initial_box_temperature=25.0)

        kalman_prediction = []
        for i in range(len(measurements_heater)):
            x = f.kalman_step(measurements_heater[i], measurements_Troom[i], measurements_T[i])
            kalman_prediction.append(x)

        kalman_prediction = np.array(kalman_prediction).squeeze(2)

        # Run experiment with model, without any filtering, just for comparison.
        results_4p, sol = run_experiment_four_parameter_model(data, params)

        fig = plotly_incubator_data(data, compare_to={
                                        "4pModel": {
                                            "time": results_4p.signals["time"],
                                            "T": results_4p.signals["T"],
                                        },
                                        "Kalman": {
                                            "time": time,
                                            "T": kalman_prediction[:, 1]
                                        },
                                    },
                                    heater_T_data={
                                        "4pModel": {
                                            "time": results_4p.signals["time"],
                                            "T_heater": results_4p.signals["T_heater"],
                                        },
                                        "Kalman": {
                                            "time": time,
                                            "T_heater": kalman_prediction[:, 0]
                                        },
                                    },
                                    overlay_heater=True)

        if self.ide_mode():
            show_plotly(fig)


if __name__ == '__main__':
    unittest.main()
