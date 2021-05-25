import logging
import time

import numpy as np

from digital_twin.communication.rabbitmq_protocol import ROUTING_KEY_KF_PLANT_STATE
from incubator.communication.server.rabbitmq import Rabbitmq
from incubator.communication.shared.protocol import ROUTING_KEY_STATE
from incubator.monitoring.kalman_filter_4p import construct_filter


class KalmanFilterPlantServer:

    def __init__(self, rabbit_config):
        self._l = logging.getLogger("KalmanFilterPlantServer")
        self.filter = None
        self.rabbitmq = Rabbitmq(**rabbit_config)

    def setup(self, step_size, std_dev,
              C_air, G_box, C_heater, G_heater,
              initial_heat_temperature, initial_box_temperature):
        self.rabbitmq.connect_to_server()

        self.filter = construct_filter(step_size, std_dev,
                                       C_air, G_box, C_heater, G_heater,
                                       initial_heat_temperature, initial_box_temperature)

        self.rabbitmq.subscribe(routing_key=ROUTING_KEY_STATE,
                                on_message_callback=self.kalman_step)

    def start_monitoring(self):
        self.rabbitmq.start_consuming()

    def kalman_step(self, ch, method, properties, body_json):
        in_heater = 1.0 if body_json["fields"]["heater_on"] else 0.0
        in_room_T = body_json["fields"]["t1"]

        in_T = body_json["fields"]["average_temperature"]

        self.filter.predict(u=np.array([
            [in_heater],
            [in_room_T]
        ]))
        self.filter.update(np.array([[in_T]]))

        next_x = self.filter.x
        T_heater = next_x[0, 0]
        T = next_x[1, 0]

        timestamp = body_json["time"]

        message = {
            "measurement": "kalman_filter_plant",
            "time": timestamp,
            "tags": {
                "source": "kalman_filter_plant"
            },
            "fields": {
                "T_heater": T_heater,
                "average_temperature": T,
                "prediction_time": time.time_ns(),
            }
        }

        self.rabbitmq.send_message(ROUTING_KEY_KF_PLANT_STATE, message)
