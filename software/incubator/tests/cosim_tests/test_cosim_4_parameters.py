import unittest

from oomodelling import ModelSolver

import matplotlib.pyplot as plt

from incubator.config.config import load_config
from incubator.models.physical_twin_models.system_model4 import SystemModel4Parameters
from incubator.models.physical_twin_models.system_model4_open_loop import SystemModel4ParametersOpenLoop
from incubator.models.plant_models.four_parameters_model.best_parameters import four_param_model_params
from incubator.physical_twin.low_level_driver_server import CTRL_EXEC_INTERVAL
from incubator.visualization.data_plotting import plotly_incubator_data, show_plotly
from incubator.tests.cli_mode_test import CLIModeTest
import pandas as pd


class CosimulationTests(CLIModeTest):

    def test_run_cosim_4param_model(self):
        C_air = four_param_model_params[0]
        G_box = four_param_model_params[1]
        C_heater = four_param_model_params[2]
        G_heater = four_param_model_params[3]
        V_heater = four_param_model_params[4]
        I_heater = four_param_model_params[5]

        fig = plt.figure()

        def show_trace(heating_time):
            m = SystemModel4Parameters(C_air,
                                       G_box,
                                       C_heater,
                                       G_heater,
                                       V_heater, I_heater,
                                       lower_bound=10, heating_time=heating_time, heating_gap=2.0,
                                       temperature_desired=35, initial_box_temperature=22, initial_heat_temperature=22,
                                       initial_room_temperature=22)
            ModelSolver().simulate(m, 0.0, 3000, CTRL_EXEC_INTERVAL, CTRL_EXEC_INTERVAL / 10.0)

            plt.plot(m.signals['time'], m.plant.signals['T'], label=f"Trial_{heating_time}")

        # show_trace(0.1)
        # show_trace(1.0)
        show_trace(3.0)
        # show_trace(100.0)

        plt.legend()

        if self.ide_mode():
            plt.show()
        plt.close(fig)

    def test_fine_tune_controller(self):
        C_air_num = four_param_model_params[0]
        G_box_num = four_param_model_params[1]
        C_heater_num = four_param_model_params[2]
        G_heater_num = four_param_model_params[3]
        V_heater_num = four_param_model_params[4]
        I_heater_num = four_param_model_params[5]

        m = SystemModel4Parameters(C_air=C_air_num,
                                   G_box=G_box_num,
                                   C_heater=C_heater_num,
                                   G_heater=G_heater_num,
                                   V_heater=V_heater_num,
                                   I_heater=I_heater_num,
                                   lower_bound=10, heating_time=10.0, heating_gap=2.0,
                                   temperature_desired=35, initial_box_temperature=22, initial_heat_temperature=22,
                                   initial_room_temperature=22)
        ModelSolver().simulate(m, 0.0, 3000, CTRL_EXEC_INTERVAL, CTRL_EXEC_INTERVAL / 10.0)

        # Convert cosim data into a dataframe
        data_cosim = pd.DataFrame()
        data_cosim["time"] = m.signals['time']
        data_cosim["average_temperature"] = m.plant.signals['T']
        data_cosim["T_room"] = m.plant.signals['in_room_temperature']
        data_cosim["heater_on"] = m.plant.signals['in_heater_on']

        fig = plotly_incubator_data(data_cosim, overlay_heater=True)

        if self.ide_mode():
            show_plotly(fig)

    def test_run_cosim_4param_mode_open_loop(self):

        show_heater_signal = False

        config = load_config("startup.conf")
        n_samples_period = 40
        C_air = config["digital_twin"]["models"]["plant"]["param4"]["C_air"]
        G_box = config["digital_twin"]["models"]["plant"]["param4"]["G_box"]
        C_heater = config["digital_twin"]["models"]["plant"]["param4"]["C_heater"]
        G_heater = config["digital_twin"]["models"]["plant"]["param4"]["G_heater"]
        V_heater = config["digital_twin"]["models"]["plant"]["param4"]["V_heater"]
        I_heater = config["digital_twin"]["models"]["plant"]["param4"]["I_heater"]
        initial_box_temperature = config["digital_twin"]["models"]["plant"]["param4"]["initial_box_temperature"]
        initial_heat_temperature = config["digital_twin"]["models"]["plant"]["param4"]["initial_heat_temperature"]

        fig = plt.figure()

        def show_trace(n_samples_heating, n_samples_period):
            m = SystemModel4ParametersOpenLoop(n_samples_period,
                                               n_samples_heating,
                                               C_air,
                                               G_box,
                                               C_heater,
                                               G_heater,
                                               V_heater, I_heater,
                                               initial_box_temperature,
                                               initial_heat_temperature,
                                               initial_room_temperature=initial_box_temperature)
            ModelSolver().simulate(m, 0.0, 6000, CTRL_EXEC_INTERVAL, CTRL_EXEC_INTERVAL / 10.0)

            plt.plot(m.signals['time'], m.plant.signals['T'], label=f"NHeating_{n_samples_heating}")
            if show_heater_signal:
                plt.plot(m.signals['time'], [30 if b else 0 for b in m.ctrl.signals["heater_on"]],
                         label=f"NHeating_{n_samples_heating}")

        for n_samples_heating in range(0, 5):
            assert n_samples_heating <= n_samples_period
            show_trace(n_samples_heating, n_samples_period)

        plt.legend()

        if self.ide_mode():
            plt.show()
        plt.close(fig)


if __name__ == '__main__':
    unittest.main()
