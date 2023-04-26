import math
import unittest

import matplotlib.pyplot as plt
import pandas

from incubator.config.config import resource_file_path
from incubator.data_processing.data_processing import load_data, derive_data
from incubator.models.plant_models.model_functions import run_experiment_four_parameter_model
from incubator.tests.cli_mode_test import CLIModeTest
from incubator.visualization.data_plotting import plot_incubator_data, plotly_incubator_data, show_plotly


class TestPlotData(CLIModeTest):

    def test_plot_data_default_setup(self):
        # CWD: Example_Digital-Twin_Incubator\software\
        data, _ = load_data("./incubator/datasets/20201221_controller_tunning/exp1_ht3_hg2.csv",
                            desired_timeframe=(- math.inf, math.inf))

        plot_incubator_data(data)

        if self.ide_mode():
            plt.show()

    def test_plot_data_plotly(self):
        time_unit = 'ns'

        # time_frame = (1614859007119846022, 1614861060000000000 - 1)
        time_frame = (1614859007119846022, math.inf)

        data, events = load_data("./incubator/datasets/20210321_lid_opening_7pmodel/lid_opening_experiment_mar_2021.csv",
                                 events="./incubator/datasets/20210321_lid_opening_7pmodel/events.csv",
                                 desired_timeframe=time_frame,
                                 time_unit=time_unit,
                                 normalize_time=False,
                                 convert_to_seconds=True)

        if self.ide_mode():
            print(f"Experiment time from {data.iloc[0]['timestamp_ns']} to {data.iloc[-1]['timestamp_ns']}")

        # Rename column to make data independent of specific tN's
        data.rename(columns={"t1": "T_room"}, inplace=True)

        params4pmodel = [145.69782402,  # C_air
                         0.79154106,  # G_box
                         227.76228512,  # C_heater
                         1.92343277]  # G_heater
        results4p, sol = run_experiment_four_parameter_model(data, params4pmodel)

        fig = plotly_incubator_data(data, compare_to={
            "T(4)": {
                "time": results4p.signals["time"],
                "timestamp_ns": pandas.to_datetime(results4p.signals["time"], unit='s'),
                "T": results4p.signals["T"],
            }
        }, events=events, overlay_heater=True, show_hr_time=True)

        if self.ide_mode():
            show_plotly(fig)

    def test_plot_mar_experiment(self):
        time_unit = 'ns'
        data, events = load_data("./incubator/datasets/20210321_lid_opening_7pmodel/lid_opening_experiment_mar_2021.csv",
                                 events="./incubator/datasets/20210321_lid_opening_7pmodel/events.csv",
                                 desired_timeframe=(- math.inf, math.inf),
                                 time_unit=time_unit,
                                 normalize_time=False,
                                 convert_to_seconds=True)

        if self.ide_mode():
            print(f"Experiment time from {data.iloc[0]['timestamp_ns']} to {data.iloc[-1]['timestamp_ns']}")

        # Rename column to make data independent of specific tN's
        data.rename(columns={"t1": "T_room"}, inplace=True)

        params4pmodel = [145.69782402,  # C_air
                         0.79154106,  # G_box
                         227.76228512,  # C_heater
                         1.92343277]  # G_heater
        results4p, sol = run_experiment_four_parameter_model(data, params4pmodel)

        fig = plotly_incubator_data(data, compare_to={
            "T(4)": {
                "timestamp_ns": pandas.to_datetime(results4p.signals["time"], unit='s'),
                "T": results4p.signals["T"],
            }
        }, events=events, overlay_heater=True, show_hr_time=True)

        if self.ide_mode():
            show_plotly(fig)

    def test_plot_202304_new_heater(self):
        time_unit = 'ns'
        data, events = load_data("./rec_2023-04-22__13_17_04.csv",
                                 # events="./incubator/datasets/20210321_lid_opening_7pmodel/events.csv",
                                 desired_timeframe=(- math.inf, math.inf),
                                 time_unit=time_unit,
                                 normalize_time=False,
                                 convert_to_seconds=True)

        # Rename column to make data independent of specific tN's
        data.rename(columns={"t3": "T_room"}, inplace=True)

        if self.ide_mode():
            print(f"Experiment time from {data.iloc[0]['timestamp_ns']} to {data.iloc[-1]['timestamp_ns']}")

        fig = plotly_incubator_data(data, events=events, overlay_heater=True)

        if self.ide_mode():
            show_plotly(fig)


if __name__ == '__main__':
    unittest.main()
