import matplotlib.pyplot as plt
from oomodelling import ModelSolver

from incubator.models.physical_twin_models.system_model4 import SystemModel4Parameters
from incubator.models.plant_models.four_parameters_model.best_parameters import four_param_model_params
from incubator.physical_twin.low_level_driver_server import CTRL_EXEC_INTERVAL
from incubator.tests.cli_mode_test import CLIModeTest
import numpy as np
from typing import List


def control_error(time: List[float], actual_temperature_signal: List[float], temperature_desired: float):
    """
    Calculates the controller error, which is the integral of the absolute error over time between the temperature
                desired the actual temperature
    """
    assert len(time) == len(actual_temperature_signal)
    actual_temperature_array = np.array(actual_temperature_signal)
    time_array = np.array(time)
    temp_difference = np.abs(temperature_desired - actual_temperature_array)
    integral = np.trapz(temp_difference, time_array)
    return integral


def run_experiment(temperature_desired, bound, heating_time, heating_gap, time_final):
    upper_bound = temperature_desired + bound
    lower_bound = 2 * bound
    C_air = four_param_model_params[0]
    G_box = four_param_model_params[1]
    C_heater = four_param_model_params[2]
    G_heater = four_param_model_params[3]
    V_heater = four_param_model_params[4]
    I_heater = four_param_model_params[5]

    m = SystemModel4Parameters(C_air,
                               G_box,
                               C_heater,
                               G_heater,
                               V_heater, I_heater,
                               lower_bound, heating_time, heating_gap,
                               upper_bound,
                               initial_box_temperature=temperature_desired,
                               initial_heat_temperature=temperature_desired,
                               initial_room_temperature=22.0)

    ModelSolver().simulate(m, 0.0, time_final, CTRL_EXEC_INTERVAL, CTRL_EXEC_INTERVAL / 10.0)

    return m


class TestControllerTunning(CLIModeTest):
    def test_controller_manual_space_exploration(self):
        """
        This demonstrates the trade-offs involved in tuning the controller parameters.
        """

        fig = plt.figure()

        # illustrate the tradeoff
        bound_1 = 10.0
        bound_2 = 1.0
        temp_desired = 38.0
        heating_gap = 3.0
        time_final = 5000 if self.ide_mode() else 1000
        m_1 = run_experiment(temp_desired, bound_1, 20000, heating_gap, time_final)
        plt.plot(m_1.signals['time'], m_1.plant.signals['T'], label=f"m_1_T")
        plt.plot(m_1.signals['time'], m_1.ctrl.signals['heater_on'], label=f"m_1_H")

        m_2 = run_experiment(temp_desired, bound_2, 20000, heating_gap, time_final)
        plt.plot(m_2.signals['time'], m_2.plant.signals['T'], label=f"m_2_T")
        plt.plot(m_2.signals['time'], m_2.ctrl.signals['heater_on'], label=f"m_2_H")

        ctrl_error_bad = control_error(m_1.signals['time'], m_1.plant.signals['T'], temp_desired)
        ctrl_error_good = control_error(m_2.signals['time'], m_2.plant.signals['T'], temp_desired)

        actuator_effort_good = m_1.ctrl.signals['actuator_effort'][-1]
        actuator_effort_bad = m_2.ctrl.signals['actuator_effort'][-1]

        self.assertGreater(ctrl_error_bad, ctrl_error_good)
        self.assertGreater(actuator_effort_bad, actuator_effort_good)

        plt.legend()

        if self.ide_mode():
            print(f"lower_bound={bound_1} => ctrl_error={ctrl_error_bad} and actuator_effort={actuator_effort_good}")
            print(f"lower_bound={bound_2} => ctrl_error={ctrl_error_good} and actuator_effort={actuator_effort_bad}")
            plt.show()
        plt.close(fig)

    def test_controller_plot_pareto_front(self):
        """
        This builds a pareto front.
        """
        time_final = 5000 if self.ide_mode() else 1000
        resolution = 16 if self.ide_mode() else 2
        bounds = np.linspace(0.1, 10.0, resolution)
        # heating_times = np.linspace(0.1, 100, resolution)
        heating_time = 100.0
        # heating_gaps = np.linspace(0.1, 10.0, resolution)
        heating_gap = 3.0

        results = []

        temp_desired = 38.0

        # total_num_experiments = len(bounds) * len(heating_times) * len(heating_gaps)
        total_num_experiments = len(bounds)
        count = 0

        # for bound, heating_time, heating_gap in product(bounds, heating_times, heating_gaps):
        for bound in bounds:
            bound = round(bound, 2)
            if self.ide_mode():
                count += 1
                print(f"Experiment {count}/{total_num_experiments}.")
            m = run_experiment(temp_desired, bound, heating_time, heating_gap, time_final)
            ctrl_error = control_error(m.signals['time'], m.plant.signals['T'], temp_desired)
            actuator_effort = m.ctrl.signals['actuator_effort'][-1]
            results.append({
                "bound": bound,
                "heating_time": heating_time,
                "heating_gap": heating_gap,
                "ctrl_error": ctrl_error,
                "actuator_effort": actuator_effort
            })

        self.assertEqual(len(results), total_num_experiments)

        # Identify the pareto front points

        ctrl_errors = np.array([r["ctrl_error"] for r in results])
        actuator_efforts = np.array([r["actuator_effort"] for r in results])

        pareto_front_ctrl_errors = []
        pareto_front_actuator_efforts = []
        pareto_front_parameters = []

        for i in range(len(ctrl_errors)):
            is_pareto = True
            for j in range(len(ctrl_errors)):
                if (ctrl_errors[j] <= ctrl_errors[i] and actuator_efforts[j] < actuator_efforts[i]) or \
                        (ctrl_errors[j] < ctrl_errors[i] and actuator_efforts[j] <= actuator_efforts[i]):
                    is_pareto = False
                    break
            if is_pareto:
                pareto_front_ctrl_errors.append(ctrl_errors[i])
                pareto_front_actuator_efforts.append(actuator_efforts[i])
                pareto_front_parameters.append(results[i])

        fig = plt.figure()

        plt.scatter(ctrl_errors, actuator_efforts, c='b', label='Controller Policy')
        plt.scatter(pareto_front_ctrl_errors, pareto_front_actuator_efforts, c='g', label='Pareto Front')

        plt.xlabel('Controller Error')
        plt.ylabel('Actuator Effort')

        for r in pareto_front_parameters:
            plt.annotate(f'b={r["bound"]}',
                         xy=(r["ctrl_error"], r["actuator_effort"]),
                         arrowprops=dict(arrowstyle='->'),
                         fontsize=14)

        plt.legend()

        if self.ide_mode():
            plt.savefig("dse_incubator.svg")
            print(pareto_front_parameters)
            plt.show()

        plt.close(fig)
