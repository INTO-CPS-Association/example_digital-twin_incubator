from oomodelling import Model

from incubator.models.physical_twin_models.system_model4_open_loop import SystemModel4ParametersOpenLoop
from incubator.self_adaptation.self_adaptation_manager import SelfAdaptationModel, SelfAdaptationManager
from incubator.monitoring.kalman_filter_4p import KalmanFilter4P
from incubator.self_adaptation.supervisor import SupervisorModel, ISupervisorSM


class SelfAdaptationScenario(Model):
    def __init__(self,
                 # Initial Controller parameters
                 n_samples_period, n_samples_heating,
                 # Plant parameters
                 C_air,
                 G_box,
                 C_heater,
                 G_heater,
                 V_heater, I_heater,
                 initial_box_temperature,
                 initial_heat_temperature,
                 initial_room_temperature,
                 kalman: KalmanFilter4P,
                 self_adaptation_manager: SelfAdaptationManager,
                 supervisor_sm: ISupervisorSM
                 ):
        super().__init__()

        self.physical_twin = SystemModel4ParametersOpenLoop(n_samples_period,
                                                            n_samples_heating,
                                                            C_air,
                                                            G_box,
                                                            C_heater,
                                                            G_heater,
                                                            V_heater, I_heater,
                                                            initial_box_temperature,
                                                            initial_heat_temperature,
                                                            initial_room_temperature)

        self.kalman = kalman
        self.self_adaptation_manager = SelfAdaptationModel(self_adaptation_manager)
        self.supervisor = SupervisorModel(supervisor_sm)

        # Plant --> KF
        # self.noise_sensor = NoiseFeedthrough(std_dev)
        # self.noise_sensor.u = self.physical_twin.plant.T
        # self.kalman.in_T = self.noise_sensor.y
        self.kalman.in_T = self.physical_twin.plant.T
        self.kalman.in_heater_on = self.physical_twin.ctrl.heater_on

        # KF --> AnomalyDetector
        self.self_adaptation_manager.predicted_temperature = self.kalman.out_T
        # Plant --> AnomalyDetector
        self.self_adaptation_manager.real_temperature = self.physical_twin.plant.T

        # KF --> Supervisor
        self.supervisor.T = self.kalman.out_T
        self.supervisor.T_heater = self.kalman.out_T_heater

        self.save()
