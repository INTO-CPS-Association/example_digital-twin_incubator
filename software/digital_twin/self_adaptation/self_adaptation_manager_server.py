import logging

from incubator.communication.server.rabbitmq import Rabbitmq
from digital_twin.communication.rabbitmq_protocol import ROUTING_KEY_KF_PLANT_STATE
from incubator.communication.shared.protocol import ROUTING_KEY_STATE


class SelfAdaptationManagerServer:

    def __init__(self, rabbit_config):
        self._l = logging.getLogger("SelfAdaptationManagerServer")
        self.filter = None
        self.rabbitmq = Rabbitmq(**rabbit_config)
        self.sm = SelfAdaptationManagerSM(self.step_self_adaptation)

    def setup(self):
        self.rabbitmq.connect_to_server()

        self.rabbitmq.subscribe(routing_key=ROUTING_KEY_STATE,
                                on_message_callback=self.consume_state_message)
        self.rabbitmq.subscribe(routing_key=ROUTING_KEY_KF_PLANT_STATE,
                                on_message_callback=self.consume_kalmanfilter_message)

    def start(self):
        self.rabbitmq.start_consuming()

    def consume_state_message(self, ch, method, properties, body_json):
        self._l.debug("State message received: ")
        self._l.debug(body_json)
        self.sm.step(body_json)

    def consume_kalmanfilter_message(self, ch, method, properties, body_json):
        self._l.debug("Kalman Filter message received: ")
        self._l.debug(body_json)
        self.sm.step(body_json)

    def step_self_adaptation(self, lld_measurement, kf_measurement):
        self._l.debug("Adaptation step")


class SelfAdaptationManagerSM:

    def __init__(self, process_complete_system_snapshot_fun):
        self.state = "Initial"
        self.lld_measurement = None
        self.kf_measurement = None
        self.process_complete_system_snapshot_fun = process_complete_system_snapshot_fun

    def step(self, body_json):
        assert body_json["measurement"] == "low_level_driver" or body_json["measurement"] == "kalman_filter_plant"

        if self.state == "Initial":
            assert self.lld_measurement is None and self.kf_measurement is None
            if body_json["measurement"] == "low_level_driver":
                self.lld_measurement = body_json
                self.state = 'ExpectingKF'
            elif body_json["measurement"] == "kalman_filter_plant":
                self.kf_measurement = body_json
                self.state = 'ExpectingLLD'
        if self.state == "ExpectingKF":
            assert self.lld_measurement is not None
            assert self.kf_measurement is None
            if body_json["measurement"] == "low_level_driver":
                self.lld_measurement = body_json
            elif body_json["measurement"] == "kalman_filter_plant":
                """
                Three scenarios can happen:
                - [Past] The new KF measurements is older than the LLD measurement
                - [Present] The new KF measurement matches the LLD measurement
                - [Future] The new KF measurement is newer the LLD measurement
                """
                if body_json["time"] < self.lld_measurement["time"]:
                    # [Past]: Disregard KF measurement and stay in the same state (ie, do nothing)
                    pass
                elif body_json["time"] == self.lld_measurement["time"]:
                    # [Present]: We have a complete picture of the system, so we move to the next stage.
                    self.kf_measurement = body_json
                    self.process_complete_system_snapshot()
                elif body_json["time"] > self.lld_measurement["time"]:
                    # [Future]: Disregard LLD measurement and to go corresponding state
                    self.kf_measurement = body_json
                    self.lld_measurement = None
                    self.state = 'ExpectingLLD'
            return
        if self.state == "ExpectingLLD":
            assert self.lld_measurement is None
            assert self.kf_measurement is not None
            if body_json["measurement"] == "low_level_driver":
                """
                Three scenarios can happen:
                - [Past] The new LLD measurements is older than the KF measurement
                - [Present] The new LLD measurement matches the KF measurement
                - [Future] The new LLD measurement is newer the KF measurement
                """
                if body_json["time"] < self.kf_measurement["time"]:
                    # [Past]: Disregard LLD measurement and stay in the same state (ie, do nothing)
                    pass
                elif body_json["time"] == self.kf_measurement["time"]:
                    # [Present]: We have a complete picture of the system, so we move to the next stage.
                    self.lld_measurement = body_json
                    self.process_complete_system_snapshot()
                elif body_json["time"] > self.kf_measurement["time"]:
                    # [Future]: Disregard LLD measurement and to go corresponding state
                    self.lld_measurement = body_json
                    self.kf_measurement = None
                    self.state = 'ExpectingKF'
            elif body_json["measurement"] == "kalman_filter_plant":
                self.kf_measurement = body_json
            return

    def process_complete_system_snapshot(self):
        assert self.kf_measurement["time"] == self.lld_measurement["time"]
        self.process_complete_system_snapshot_fun(self.lld_measurement, self.kf_measurement)
        self.kf_measurement = None
        self.lld_measurement = None
        self.state = "Initial"

