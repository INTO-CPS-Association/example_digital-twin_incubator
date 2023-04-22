import numpy as np
from matplotlib import pyplot as plt

from digital_twin.simulator.plant_simulator import PlantSimulator4Params
from incubator.models.physical_twin_models.system_model4_open_loop import SystemModel4ParametersOpenLoopSimulator
from incubator.tests.cli_mode_test import CLIModeTest


class TestSimulateReferenceSignals(CLIModeTest):

    def test_bug_shown_by_thomas(self):
        """
        This bug occurs in the calibrator, when a simulation is run with control signals as reference.
        So to reproduce it, we run a simulation, then use those as simulation results for a second simulation
        """
        pt_simulator = SystemModel4ParametersOpenLoopSimulator()
        plant_simulator = PlantSimulator4Params()

        initial_T = 20.0
        initial_T_heater = 20.0
        initial_room_T = 21.0
        parameter = 1.0
        step_size = 3.0

        model = pt_simulator.run_simulation(0.0, 15.0,
                                            initial_T, initial_T_heater, initial_room_T,
                                            5, 10, step_size,
                                            parameter, parameter, parameter, parameter)

        sol, plant_model = plant_simulator.run_simulation(model.signals["time"],
                                       initial_T, initial_T_heater,
                                       model.plant.signals['in_room_temperature'], model.ctrl.signals['heater_on'],
                                       parameter, parameter, parameter, parameter)

        self.assertEqual(len(model.signals["time"]), len(sol.y[0, :]))
        self.assertGreaterEqual(5, np.sum(np.abs(sol.y[2, :] - np.array(model.plant.signals['T_heater']))))

        fig, (ax1, ax2, ax3) = plt.subplots(3, 1)

        ax1.scatter(model.signals["time"], model.plant.signals['T_heater'], label='T_heater', alpha=0.5)
        ax1.scatter(sol.y[0,:], sol.y[2,:], label='~ sol T_heater', alpha=0.5)
        ax1.scatter(plant_model.signals["time"], plant_model.signals['T_heater'], label='~T_heater', alpha=0.5)

        ax2.scatter(model.signals["time"], model.ctrl.signals['heater_on'], label="heater_on")
        ax2.scatter(model.plant.signals["time"], model.plant.signals['in_heater_on'], label="~heater_on")

        ax3.scatter(model.signals["time"], model.signals["time"], label="t")
        ax3.scatter(model.signals["time"], sol.y[0,:], label='~ sol t')
        ax3.scatter(model.signals["time"], model.plant.signals["time"], label="~t")

        ax1.legend()
        ax2.legend()
        ax3.legend()

        if self.ide_mode():
            plt.show()

        plt.close(fig)

