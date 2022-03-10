import logging

from influxdb_client import InfluxDBClient

from digital_twin.communication.rabbitmq_protocol import ROUTING_KEY_KF_PLANT_STATE
from digital_twin.self_adaptation.self_adaptation_manager_server import DatabaseFacade, ParametricControllerFacade
from incubator.communication.server.rabbitmq import Rabbitmq
from incubator.communication.shared.protocol import from_ns_to_s
from models.physical_twin_models.system_model4_open_loop import SystemModel4ParametersOpenLoopSimulator
from self_adaptation.controller_optimizer import ControllerOptimizer
from self_adaptation.supervisor import SupervisorSM


class SupervisorServer:

    def __init__(self, rabbit_config, influxdb_config, pt_config, dt_config):
        self._l = logging.getLogger("SupervisorServer")
        self.filter = None
        self.rabbitmq = Rabbitmq(**rabbit_config)
        self.dbclient = InfluxDBClient(**influxdb_config)
        self._influxdb_bucket = influxdb_config["bucket"]
        self._influxdb_org = influxdb_config["org"]

        # TODO: Move to config files.
        conv_xatol = 0.1
        conv_fatol = 0.1
        max_iterations = 200
        desired_temperature = 38
        max_t_heater = 60
        restrict_T_heater = True

        trigger_optimization_threshold = 10.0
        wait_til_supervising_timer = 10  # N steps supervisor should wait before kicking in.

        database = DatabaseFacade(self.dbclient, self._influxdb_bucket, self._influxdb_org,
                                  dt_config["models"]["plant"]["param4"], pt_config["controller_open_loop"])

        # TODO: Invoke actual calibrator service, when the system is working.
        ctrl = ParametricControllerFacade(self.rabbitmq)

        pt_simulator = SystemModel4ParametersOpenLoopSimulator()
        ctrl_optimizer = ControllerOptimizer(database, pt_simulator, ctrl, conv_xatol, conv_fatol, max_iterations,
                                             restrict_T_heater, desired_temperature, max_t_heater)

        self.sm = SupervisorSM(ctrl_optimizer, desired_temperature, max_t_heater, restrict_T_heater,
                                  trigger_optimization_threshold, wait_til_supervising_timer)

    def setup(self):
        self.rabbitmq.connect_to_server()

        self.rabbitmq.subscribe(routing_key=ROUTING_KEY_KF_PLANT_STATE,
                                on_message_callback=self.consume_kalmanfilter_message)

    def start(self):
        self.rabbitmq.start_consuming()

    def consume_kalmanfilter_message(self, ch, method, properties, body_json):
        self._l.debug("Kalman Filter message received: ")
        self._l.debug(body_json)
        T = body_json["fields"]["average_temperature"]
        T_heater = body_json["fields"]["T_heater"]
        time_ns = body_json["time"]
        time_s = from_ns_to_s(time_ns)

        self.sm.step(T, T_heater, time_s)
