import time

from communication.server.rabbitmq import Rabbitmq, ROUTING_KEY_STATE, ROUTING_KEY_KF_PLANT_STATE
from communication.server.rpc_server import *
from digital_twin.monitoring.kalman_filter_4p import construct_filter
import numpy as np


class KalmanFilterPlantServer():

    def __init__(self, ip=RASPBERRY_IP):
        self._l = logging.getLogger("KalmanFilterPlantServer")
        self.filter = None
        self.rabbitmq = Rabbitmq(ip=ip)

    def start_monitoring(self, step_size, std_dev,
                         C_air, G_box, C_heater, G_heater,
                         initial_heater_temperature, initial_box_temperature):
        self.rabbitmq.connect_to_server()

        self.filter = construct_filter(step_size, std_dev,
                                       C_air, G_box, C_heater, G_heater,
                                       initial_heater_temperature, initial_box_temperature)
        try:
            self.rabbitmq.subscribe(routing_key=ROUTING_KEY_STATE,
                                    on_message_callback=self.kalman_step)
            self.rabbitmq.start_consuming()
        except:
            self._l.warning("Stopping Kalman filter")
            self.rabbitmq.close()
            raise

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
