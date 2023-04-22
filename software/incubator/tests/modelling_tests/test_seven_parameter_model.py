import logging
import math
import unittest
from copy import copy

import numpy as np
import pandas
from scipy.optimize import leastsq, least_squares

from incubator.data_processing.data_processing import load_data, derive_data
from incubator.models.plant_models.four_parameters_model.best_parameters import four_param_model_params
from incubator.models.plant_models.model_functions import run_experiment_seven_parameter_model, construct_residual, \
    run_experiment_four_parameter_model, run_experiment_two_parameter_model
from incubator.models.plant_models.seven_parameters_model.best_parameters import seven_param_model_params
from incubator.models.plant_models.two_parameters_model.best_parameters import two_param_model_params
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
        guess[0] = guess[0] if self.ide_mode() else guess[0] + 0.1 # Just to make the thing converge

        added_cup_event_ts = 1614867211000000000
        first_lid_open_event = 1614861060000000000

        desired_timeframe = (-math.inf, added_cup_event_ts-1)
        time_unit = 'ns'
        convert_to_seconds = True

        h = CTRL_EXEC_INTERVAL

        data, events = load_data("./incubator/datasets/lid_opening_experiment_mar_2021/lid_opening_experiment_mar_2021.csv",
                                 events="./incubator/datasets/lid_opening_experiment_mar_2021/events.csv",
                                 desired_timeframe=desired_timeframe, time_unit=time_unit,
                                 normalize_time=False,
                                 convert_to_seconds=convert_to_seconds)

        T_heater_0 = data.iloc[0]["average_temperature"]

        def run_exp(params):
            m, sol = run_experiment_seven_parameter_model(data, params, T_heater_0, h=h)
            return m, sol, data

        residual = construct_residual([run_exp])

        sol = least_squares(residual, guess, max_nfev=NEvals)

        l.info(f"Cost: {sol.cost}")
        l.info(f"Params: {sol.x}")


    def test_calibrate_seven_parameter_model_stages(self):

        NEvals = 50 if self.ide_mode() else 1

        NStages = 8 if self.ide_mode() else 1

        desired_timeframe = (-math.inf, math.inf)
        time_unit = 'ns'
        convert_to_seconds = True

        h = CTRL_EXEC_INTERVAL

        data, events = load_data("./incubator/datasets/lid_opening_experiment_mar_2021/lid_opening_experiment_mar_2021.csv",
                                 events="./incubator/datasets/lid_opening_experiment_mar_2021/events.csv",
                                 desired_timeframe=desired_timeframe, time_unit=time_unit,
                                 normalize_time=False,
                                 convert_to_seconds=convert_to_seconds)

        # Isolate sections where the calibration will be run.
        stages = []
        next_stage_start = 0
        next_stage_end = 0
        next_stage_lid_open = False
        for idx, row in data.iterrows():
            start_new_stage = ((not next_stage_lid_open) and row["lid_open"] > 0.5) or \
                              (next_stage_lid_open and row["lid_open"] < 0.5)
            if start_new_stage:
                stages.append((next_stage_lid_open, next_stage_start, next_stage_end))
                next_stage_start = next_stage_end + 1
                next_stage_end = next_stage_start
                next_stage_lid_open = row["lid_open"] > 0.5
            else:
                next_stage_end += 1

        # Run calibration for each section sequentially.
        experiments = []
        for i in range(min(NStages, len(stages))):
            (lid_open, start, end) = stages[i]
            if i == 0:
                T_heater_0 = data.iloc[0]["average_temperature"]
                last_params = seven_param_model_params
            else:
                # Run last experiment and get T_heater final.
                (last_data_stage, last_params, last_T_heater_0) = experiments[-1]
                m, sol = run_experiment_seven_parameter_model(last_data_stage, last_params, last_T_heater_0, h=h)
                T_heater_0 = m.signals["T_heater"][-1]

            # Filter data to range
            data_stage = data.iloc[range(start, end)]

            # Get best parameters so far from the experiment
            params = copy(last_params)

            if lid_open:
                def run_exp_lid(param_lid):
                    params[6] = param_lid[0]
                    m, sol = run_experiment_seven_parameter_model(data_stage, params, T_heater_0, h=h)
                    return m, sol, data_stage

                residual = construct_residual([run_exp_lid])
                sol = least_squares(residual, np.array([params[6]]), max_nfev=NEvals)

                params[6] = sol.x[0]

                l.info(f"Calibration for stage {i} with lid open done.")
            else:
                def run_exp_nolid(params_nolid):
                    params[0] = params_nolid[0]
                    params[1] = params_nolid[1]
                    params[2] = params_nolid[2]
                    params[3] = params_nolid[3]
                    m, sol = run_experiment_seven_parameter_model(data_stage, params, T_heater_0, h=h)
                    return m, sol, data_stage

                residual = construct_residual([run_exp_nolid])
                sol = least_squares(residual, np.array([params[i] for i in range(4)]), max_nfev=NEvals)

                params[0] = sol.x[0]
                params[1] = sol.x[1]
                params[2] = sol.x[2]
                params[3] = sol.x[3]

                l.info(f"Calibration for stage {i} with no lid open done.")

            l.info(f"Cost: {sol.cost}")
            l.info(f"Params: {sol.x}")

            experiments.append((data_stage, params, T_heater_0))

        l.info(f"Calibration done. Final results:")
        (_, last_params, _) = experiments[-1]
        l.info(last_params)

    def test_run_experiment_seven_parameter_model(self):
        time_unit = 'ns'

        tf = math.inf if self.ide_mode() else 1614867211000000000-1
        tf = 1614867210000000000 + 1 if self.ide_mode() else 1614867211000000000 - 1

        # CWD: Example_Digital-Twin_Incubator\software\
        data, events = load_data("./incubator/datasets/lid_opening_experiment_mar_2021/lid_opening_experiment_mar_2021.csv",
                                 events="./incubator/datasets/lid_opening_experiment_mar_2021/events.csv",
                                 desired_timeframe=(-math.inf, tf),
                                 time_unit=time_unit,
                                 normalize_time=False,
                                 convert_to_seconds=True)
        params = seven_param_model_params

        results, sol = run_experiment_seven_parameter_model(data, params, initial_heat_temperature=data.iloc[0]["average_temperature"])

        results_4, sol_4 = run_experiment_four_parameter_model(data, four_param_model_params)

        results_2p, sol_2p = run_experiment_two_parameter_model(data, two_param_model_params)

        l.info(f"Experiment time from {data.iloc[0]['timestamp_ns']} to {data.iloc[-1]['timestamp_ns']}")

        fig = plotly_incubator_data(data,
                                    compare_to={
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
                                    },
                                    events=events,
                                    overlay_heater=False,
                                    show_actuators=True,
                                    show_hr_time=True
                                    )

        if self.ide_mode():
            show_plotly(fig)
            # fig.write_image("lid_opening_experiment_mar_2p_4p_7p.svg")


if __name__ == '__main__':
    unittest.main()
