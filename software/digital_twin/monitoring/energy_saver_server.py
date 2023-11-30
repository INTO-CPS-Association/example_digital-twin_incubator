import logging

from digital_twin.communication.rabbitmq_protocol import ROUTING_KEY_KF_PLANT_STATE
from incubator.communication.server.rabbitmq import Rabbitmq
from incubator.communication.shared.protocol import ROUTING_KEY_UPDATE_CLOSED_CTRL_PARAMS


class EnergySaverServer:

    def __init__(self, error_threshold, ctrl_config_baseline, rabbit_config):
        self._l = logging.getLogger("EnergySaverServer")
        self.filter = None
        self.rabbitmq = Rabbitmq(**rabbit_config)

        self.in_prediction_error = 0.0
        self.error_threshold = error_threshold

        self.ctrl_temperature_desired = ctrl_config_baseline['temperature_desired']

    def setup(self):
        self.rabbitmq.connect_to_server()

        self.rabbitmq.subscribe(routing_key=ROUTING_KEY_KF_PLANT_STATE,
                                on_message_callback=self.kalman_step)

    def start_monitoring(self):
        self.rabbitmq.start_consuming()

    def kalman_step(self, ch, method, properties, body_json):
        self.in_prediction_error = body_json["fields"]["prediction_error"]

        new_temp_desired = self.ctrl_temperature_desired*0.6 if abs(self.in_prediction_error) > self.error_threshold else self.ctrl_temperature_desired

        self._l.debug(f"Updating closed loop controller temperature desired to: {new_temp_desired} due to error {abs(self.in_prediction_error)}.")
        self.rabbitmq.send_message(ROUTING_KEY_UPDATE_CLOSED_CTRL_PARAMS, {
            "temperature_desired": new_temp_desired,
        })