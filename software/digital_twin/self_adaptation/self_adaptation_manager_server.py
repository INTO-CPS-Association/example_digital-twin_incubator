import logging

from incubator.communication.server.rabbitmq import Rabbitmq
from digital_twin.communication.rabbitmq_protocol import ROUTING_KEY_KF_PLANT_STATE
from incubator.communication.shared.protocol import ROUTING_KEY_STATE


class SelfAdaptationManagerServer:

    def __init__(self, rabbit_config):
        self._l = logging.getLogger("SelfAdaptationManagerServer")
        self.filter = None
        self.rabbitmq = Rabbitmq(**rabbit_config)

    def setup(self):
        self.rabbitmq.connect_to_server()

        self.rabbitmq.subscribe(routing_key=ROUTING_KEY_STATE,
                                on_message_callback=self.comsume_state_message)
        self.rabbitmq.subscribe(routing_key=ROUTING_KEY_KF_PLANT_STATE,
                                on_message_callback=self.comsume_kalmanfilter_message)

    def start(self):
        self.rabbitmq.start_consuming()

    def comsume_state_message(self, ch, method, properties, body_json):
        self._l.debug("State message received: ")
        self._l.debug(body_json)

    def comsume_kalmanfilter_message(self, ch, method, properties, body_json):
        self._l.debug("Kalman Filter message received: ")
        self._l.debug(body_json)

