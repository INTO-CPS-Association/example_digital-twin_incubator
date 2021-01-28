import math
import os
import tempfile
import unittest

import matplotlib.pyplot as plt
import pandas

from digital_twin.data_processing.data_processing import load_data
from digital_twin.fsutils import resource_file_path
from digital_twin.models.plant_models.model_functions import run_experiment_four_parameter_model, \
    run_experiment_two_parameter_model
from digital_twin.visualization.data_plotting import plot_incubator_data, plotly_incubator_data, show_plotly
from tests.cli_mode_test import CLIModeTest


class TestPlotData(CLIModeTest):

    def test_plot_data_default_setup(self):
        # CWD: Example_Digital-Twin_Incubator\software\
        data = load_data("../datasets/controller_tunning/exp1_ht3_hg2.csv",
                         desired_timeframe=(- math.inf, math.inf))

        plot_incubator_data(data)

        if self.ide_mode():
            plt.show()

    def test_plot_data_plotly(self):
        time_unit = 'ns'
        data = load_data("../datasets/lid_opening_experiment_jan_2021/lid_opening_experiment_jan_2021.csv",
                         desired_timeframe=(- math.inf, math.inf),
                         time_unit=time_unit)
        events = pandas.read_csv(resource_file_path("../datasets/lid_opening_experiment_jan_2021/events.csv"))
        events["timestamp"] = pandas.to_datetime(events["time"], unit=time_unit)

        if self.ide_mode():
            print(f"Experiment time from {data.iloc[0]['timestamp']} to {data.iloc[-1]['timestamp']}")

        params4pmodel = [145.69782402,  # C_air
                         0.79154106,  # G_box
                         227.76228512,  # C_heater
                         1.92343277]  # G_heater
        # results4p, sol = run_experiment_four_parameter_model(data, params4pmodel)

        params2pmodel = [616.56464029,  # C_air
                         0.65001889]  # G_box
        # results2p, sol = run_experiment_two_parameter_model(data, params2pmodel)

        fig = plotly_incubator_data(data,
                                    # compare_to={
                                    #     "T(4)": {
                                    #         "time": results4p.signals["time"],
                                    #         "T": results4p.signals["T"],
                                    #     },
                                    #     # "T(2)": {
                                    #     #     "time": results2p.signals["time"],
                                    #     #     "T": results2p.signals["T"],
                                    #     # },
                                    # },
                                    events=events,
                                    overlay_heater=True,
                                    # show_sensor_temperatures=True,
                                    show_hr_time=True
                                    )

        if self.ide_mode():
            show_plotly(fig)


if __name__ == '__main__':
    unittest.main()
