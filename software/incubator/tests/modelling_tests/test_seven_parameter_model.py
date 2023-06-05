import logging
import math
import unittest

import numpy as np
import pandas
from scipy.optimize import least_squares

from incubator.data_processing.data_processing import load_data, derive_data
from incubator.models.plant_models.four_parameters_model.best_parameters import four_param_model_params
from incubator.models.plant_models.model_functions import run_experiment_seven_parameter_model, construct_residual, \
    run_experiment_four_parameter_model, run_experiment_two_parameter_model
from incubator.models.plant_models.seven_parameters_model.best_parameters import seven_param_model_params
from incubator.physical_twin.low_level_driver_server import CTRL_EXEC_INTERVAL
from incubator.tests.cli_mode_test import CLIModeTest
from incubator.visualization.data_plotting import plotly_incubator_data, show_plotly

l = logging.getLogger("SevenParameterModelTests")


class SevenParameterModelTests(CLIModeTest):

    def setUp(self) -> None:
        logging.basicConfig(level=(logging.INFO if self.ide_mode() else logging.WARN))

    def test_calibrate_seven_parameter_model(self):

        NEvals = 100 if self.ide_mode() else 1

        guess = np.array(seven_param_model_params)
        guess[0] = guess[0] if self.ide_mode() else guess[0] + 0.1  # Just to make the thing converge

        added_cup_event_ts = 1614867211000000000
        first_lid_open_event = 1614861060000000000

        desired_timeframe = (-math.inf, first_lid_open_event-1)
        time_unit = 'ns'
        convert_to_seconds = True

        h = CTRL_EXEC_INTERVAL

        data, events = load_data("./incubator/datasets/20210321_lid_opening_7pmodel/lid_opening_experiment_mar_2021.csv",
                                 # events="./incubator/datasets/20210321_lid_opening_7pmodel/events.csv",
                                 desired_timeframe=desired_timeframe, time_unit=time_unit,
                                 normalize_time=False,
                                 convert_to_seconds=convert_to_seconds)
        data = derive_data(data, V_heater=guess[7], I_Heater=guess[8],
                           avg_function=lambda row: np.mean([row.t2, row.t3]))
        # Rename column to make data independent of specific tN's
        data.rename(columns={"t1": "T_room"}, inplace=True)

        T_heater_0 = data.iloc[0]["average_temperature"]

        def run_exp(params):
            m, sol = run_experiment_seven_parameter_model(data, params, T_heater_0, h=h)
            return m, sol, data

        residual = construct_residual([run_exp])

        sol = least_squares(residual, guess, max_nfev=NEvals)

        l.info(f"Cost: {sol.cost}")
        l.info(f"Params: {sol.x}")

    def test_run_experiment_seven_parameter_model(self):
        time_unit = 'ns'

        tf = math.inf if self.ide_mode() else 1614867211000000000-1
        tf = 1614867210000000000 + 1 if self.ide_mode() else 1614867211000000000 - 1

        # CWD: Example_Digital-Twin_Incubator\software\
        data, events = load_data("./incubator/datasets/20210321_lid_opening_7pmodel/lid_opening_experiment_mar_2021.csv",
                                 events="./incubator/datasets/20210321_lid_opening_7pmodel/events.csv",
                                 desired_timeframe=(-math.inf, tf),
                                 time_unit=time_unit,
                                 normalize_time=False,
                                 convert_to_seconds=True)
        params = seven_param_model_params
        data = derive_data(data, V_heater=params[7], I_Heater=params[8],
                           avg_function=lambda row: np.mean([row.t2, row.t3]))
        # Rename column to make data independent of specific tN's
        data.rename(columns={"t1": "T_room"}, inplace=True)

        results, sol = run_experiment_seven_parameter_model(data, params, initial_heat_temperature=data.iloc[0]["average_temperature"])

        results_4, sol_4 = run_experiment_four_parameter_model(data, four_param_model_params)

        two_param_params = [
            616.56464029,  # C_air
            0.65001889,  # G_box
            12.0,  # V_heater
            10.0,  # I_heater
        ]

        results_2p, sol_2p = run_experiment_two_parameter_model(data, two_param_params)

        l.info(f"Experiment time from {data.iloc[0]['timestamp_ns']} to {data.iloc[-1]['timestamp_ns']}")

        fig = plotly_incubator_data(data, compare_to={
            "T(7)": {
                "timestamp_ns": pandas.to_datetime(results.signals["time"], unit='s'),
                "T": results.signals["T"],
                # "T_object": results.signals["T_object"],
                "in_lid_open": results.signals["in_lid_open"],
            },
            "T(4)": {
                "timestamp_ns": pandas.to_datetime(results_4.signals["time"], unit='s'),
                "T": results_4.signals["T"]
            },
            "T(2)": {
                "timestamp_ns": pandas.to_datetime(results_2p.signals["time"], unit='s'),
                "T": results_2p.signals["T"]
            }
        }, events=events, overlay_heater=False, show_actuators=True, show_hr_time=True)

        if self.ide_mode():
            show_plotly(fig)
            # fig.write_image("lid_opening_experiment_mar_2p_4p_7p.svg")


if __name__ == '__main__':
    unittest.main()
