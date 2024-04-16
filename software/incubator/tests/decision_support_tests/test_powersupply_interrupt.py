import unittest

import matplotlib.pyplot as plt
from oomodelling import ModelSolver

from incubator.models.physical_twin_models.system_model4 import SystemModel4Parameters
from incubator.models.plant_models.four_parameters_model.best_parameters import four_param_model_params
from incubator.physical_twin.low_level_driver_server import CTRL_EXEC_INTERVAL
from incubator.tests.cli_mode_test import CLIModeTest


class TestPowerSupplyInterrupt(CLIModeTest):

    def test_show_different_alternatives(self):
        """
        This test plots multiple alternatives for heating time.
        It is used in the Digital Twin Engineering book.
        """
        powerfull_sys_parameters = [
            177.62927865,  # C_air
            0.77307655,  # G_box
            239.61236331,  # C_heater
            2.31872819,  # G_heater
            12.16,  # V_heater
            1.54,  # I_heater
        ]

        C_air = powerfull_sys_parameters[0]
        G_box = powerfull_sys_parameters[1]
        C_heater = powerfull_sys_parameters[2]
        G_heater = powerfull_sys_parameters[3]
        V_heater = powerfull_sys_parameters[4]
        I_heater = powerfull_sys_parameters[5]

        fig, axes = plt.subplots(2, 1, figsize=(15, 15))

        def show_trace(heating_time):
            m = SystemModel4Parameters(C_air,
                                       G_box,
                                       C_heater,
                                       G_heater,
                                       V_heater, I_heater,
                                       lower_bound=20, heating_time=heating_time, heating_gap=20000.0,
                                       max_temperature_desired=50, initial_box_temperature=35,
                                       initial_heat_temperature=35,
                                       initial_room_temperature=22)
            ModelSolver().simulate(m, 0.0, 4000, CTRL_EXEC_INTERVAL, CTRL_EXEC_INTERVAL / 10.0)

            axes[0].plot(m.signals['time'], m.plant.signals['T'], label=f"Temperature for H={heating_time}")

            axes[1].plot(m.signals['time'], ["On" if h else "Off" for h in m.ctrl.signals['heater_on']], label=f"Heater for H={heating_time}")

            return m

        m = show_trace(1000.0)
        show_trace(1500.0)
        show_trace(2000.0)

        axes[0].plot(m.signals['time'], [45.0 for t in m.signals['time']], linestyle='dashed', label=f"Maximal overheat temperature")
        axes[0].plot(m.signals['time'], [25.0 for t in m.signals['time']], linestyle='dashed',
                     label=f"Minimal temperature")

        axes[0].legend()
        axes[1].legend()

        axes[0].set_ylabel("Temperature (deg C)")
        axes[1].set_ylabel("Heater State")
        axes[1].set_xlabel("Time (s)")

        if self.ide_mode():
            plt.savefig("power_supply_interrupt_alternatives.svg")
            plt.show()
        plt.close(fig)

if __name__ == '__main__':
    unittest.main()
