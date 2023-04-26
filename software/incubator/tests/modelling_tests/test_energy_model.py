import math
import unittest

from matplotlib import pyplot as plt
from oomodelling import ModelSolver

from incubator.data_processing.data_processing import load_data
from incubator.models.plant_models.algebraic_models.energy_model import EnergyModel
from incubator.models.plant_models.model_functions import create_lookup_table
from incubator.physical_twin.low_level_driver_server import CTRL_EXEC_INTERVAL
from incubator.tests.cli_mode_test import CLIModeTest
from incubator.visualization.data_plotting import plotly_incubator_data, show_plotly


class TestsModelling(CLIModeTest):

    def test_check_power_supply_enough(self):
        model = EnergyModel(initial_heat_voltage=10.0, initial_heat_current=10.0)
        model.in_heater_on = lambda: True
        t0 = 0.0
        tf = 5.0
        sol = ModelSolver().simulate(model, t0, tf, 0.1, 0.01)

        plt.figure()

        plt.plot(model.signals["time"], model.signals["T"], label="T")
        plt.legend()


        plt.figure()

        plt.plot(model.signals["time"], model.signals["energy"], label="T")
        plt.legend()

        if self.ide_mode():
            plt.show()

    def test_compare_guesses_with_reality(self):
        # CWD: Example_Digital-Twin_Incubator\software\
        data, _ = load_data("./incubator/datasets/20200918_calibration_fan_24V/semi_random_movement.csv",
                            time_unit='s',
                            desired_timeframe=(-math.inf, math.inf),
                            normalize_time=False,
                            convert_to_seconds=False)

        model = EnergyModel(
            # initial_heat_current=0.6,
            T0=25.0)

        time_range = data["time"].to_numpy()

        in_heater_table = create_lookup_table(time_range, data["heater_on"].to_numpy())
        model.in_heater_on = lambda: in_heater_table(model.time())

        t0 = data.iloc[0]["time"]
        tf = data.iloc[-1]["time"]

        ModelSolver().simulate(model, t0, tf, CTRL_EXEC_INTERVAL, CTRL_EXEC_INTERVAL/10.0, t_eval=data["time"])

        # Rename column to make it compatible with plotly_incubator_data
        data["T_room"] = data["t1"]

        fig = plotly_incubator_data(data,
                                    compare_to={
                                        "T(1)": {
                                            "time": model.signals["time"],
                                            "timestamp_ns": model.signals["time"],
                                            "T": model.signals["T"],
                                        }
                                    },
                                    # events=events,
                                    overlay_heater=True,
                                    # show_sensor_temperatures=True,
                                    show_hr_time=False
                                    )

        if self.ide_mode():
            show_plotly(fig)





if __name__ == '__main__':
    unittest.main()
