import logging
import time

import numpy as np

from digital_twin.communication.rabbitmq_protocol import ROUTING_KEY_KF_PLANT_STATE, ROUTING_KEY_KF_UPDATE_PARAMETERS
from incubator.communication.server.rabbitmq import Rabbitmq
from incubator.communication.shared.protocol import ROUTING_KEY_STATE
from incubator.monitoring.kalman_filter_4p import construct_filter


class KalmanFilterPlantServer:

    def __init__(self, rabbit_config):
        self._l = logging.getLogger("KalmanFilterPlantServer")
        self.filter = None
        self.rabbitmq = Rabbitmq(**rabbit_config)

        # Keeps track of most recent measurement from plant
        self.in_heater = None
        self.in_room_T = None
        self.in_T = None
        self.step_size = None
        self.std_dev = None
        self.T_heater = None


    def setup(self, step_size, std_dev,
              C_air, G_box, C_heater, G_heater,
              initial_heat_temperature, initial_box_temperature):
        self.step_size = step_size
        self.std_dev = std_dev

        self.rabbitmq.connect_to_server()

        self.filter = construct_filter(step_size, std_dev,
                                       C_air, G_box, C_heater, G_heater,
                                       initial_heat_temperature, initial_box_temperature)

        self.rabbitmq.subscribe(routing_key=ROUTING_KEY_STATE,
                                on_message_callback=self.kalman_step)
        self.rabbitmq.subscribe(routing_key=ROUTING_KEY_KF_UPDATE_PARAMETERS,
                                on_message_callback=self.kalman_update_parameters)

    def start_monitoring(self):
        self.rabbitmq.start_consuming()

    def kalman_update_parameters(self, ch, method, properties, body_json):
        C_air = body_json["C_air"]
        G_box = body_json["G_box"]
        C_heater = body_json["C_heater"]
        G_heater = body_json["G_heater"]
        self._l.debug(f"Updating kalman filter parameters to: {C_air, G_box, C_heater, G_heater}")

        assert self.in_heater is not None
        assert self.in_room_T is not None
        assert self.in_T is not None
        assert self.std_dev is not None
        assert self.step_size is not None
        assert self.T_heater is not None

        self.filter = construct_filter(self.step_size, self.std_dev,
                                       C_air, G_box, C_heater, G_heater,
                                       self.T_heater, self.in_T)

    def kalman_step(self, ch, method, properties, body_json):
        self.in_heater = 1.0 if body_json["fields"]["heater_on"] else 0.0
        self.in_room_T = body_json["fields"]["t1"]

        self.in_T = body_json["fields"]["average_temperature"]

        self.filter.predict(u=np.array([
            [self.in_heater],
            [self.in_room_T]
        ]))
        self.filter.update(np.array([[self.in_T]]))

        next_x = self.filter.x
        self.T_heater = next_x[0, 0]
        T = next_x[1, 0]

        timestamp = body_json["time"]

        message = {
            "measurement": "kalman_filter_plant",
            "time": timestamp,
            "tags": {
                "source": "kalman_filter_plant"
            },
            "fields": {
                "T_heater": self.T_heater,
                "average_temperature": T,
                "prediction_time": time.time_ns(),
            }
        }

        self.rabbitmq.send_message(ROUTING_KEY_KF_PLANT_STATE, message)
