import time
from datetime import datetime
import logging
import numpy as np


from incubator.communication.server.rabbitmq import Rabbitmq, ROUTING_KEY_STATE, ROUTING_KEY_HEATER, ROUTING_KEY_FAN, \
    from_ns_to_s, ROUTING_KEY_CONTROLLER
from digital_twin.communication.rabbitmq_protocol import ROUTING_KEY_KF_UPDATE_PARAMETERS
from incubator.communication.shared.protocol import ROUTING_KEY_UPDATE_CTRL_PARAMS
from incubator.monitoring.kalman_filter_4p import construct_filter


class ControllerSafeKyx:
    def __init__(self, rabbit_config
                 ):
        self._l = logging.getLogger("OpenLoopControllerPhysical")

        self.box_air_temperature = None
        self.room_temperature = None
        self.heater_ctrl = None

        self.filter = None
        self.C_air = None
        self.C_heater = None
        self.G_box = None
        self.G_heater = None
        self.V_heater = None
        self.I_heater = None
        
        self.step_size = None
        self.T_heater = None
        self.std_dev = None
        self.Theater_covariance_init = None
        self.T_covariance_init = None

        self.old_heater = 0.0

        # Hard coded for now
        self.max_temp = 40
        self.min_temp = 35

        self.rabbitmq = Rabbitmq(**rabbit_config)

        self.header_written = False

    def _record_message(self, message):
        self.box_air_temperature = message['fields']['average_temperature']
        self.room_temperature = message['fields']['t3']
        self.old_heater = 1.0 if message["fields"]["heater_on"] else 0.0

    def safe_protocol(self):
        self._l.debug("Stopping Fan")
        self._set_fan_on(False)
        self._l.debug("Stopping Heater")
        self._set_heater_on(False)

    def _set_heater_on(self, on):
        self.rabbitmq.send_message(routing_key=ROUTING_KEY_HEATER, message={"heater": on})

    def _set_fan_on(self, on):
        self.rabbitmq.send_message(routing_key=ROUTING_KEY_FAN, message={"fan": on})

    def setup(self,step_size, std_dev, Theater_covariance_init, T_covariance_init,
              C_air, G_box, C_heater, G_heater, V_heater, I_heater,
              initial_heat_temperature, initial_box_temperature):
        self.rabbitmq.connect_to_server()
        self.safe_protocol()
        self._l.debug("Starting Fan")
        self._set_fan_on(True)

        self.step_size = step_size

        self.std_dev = std_dev
        self.Theater_covariance_init = Theater_covariance_init
        self.T_covariance_init = T_covariance_init

        # Parameter instatiation
        self.C_air = C_air
        self.C_heater = C_heater
        self.G_box = G_box
        self.G_heater = G_heater
        self.V_heater = V_heater
        self.I_heater = I_heater
    
        self._l.debug(f"Initial controller kalman filter parameters to: {C_air, G_box, C_heater, G_heater, V_heater, I_heater}")
        self.filter = construct_filter(step_size, std_dev, Theater_covariance_init, T_covariance_init,
                                       C_air, G_box, C_heater, G_heater, V_heater, I_heater,
                                       initial_heat_temperature, initial_box_temperature)
        
        self.rabbitmq.subscribe(routing_key=ROUTING_KEY_UPDATE_CTRL_PARAMS,
                                on_message_callback=self.update_parameters)
        self.rabbitmq.subscribe(routing_key=ROUTING_KEY_STATE,
                                on_message_callback=self.control_loop_callback)
        
    def kalman_prediction(self):
        self.filter.predict(u=np.array([
            [self.old_heater],
            [self.room_temperature]
        ]))
        self.filter.update(np.array([[self.box_air_temperature]]))
        next_x = self.filter.x
        self.T_heater = next_x[0, 0]

    def ctrl_step(self):
        if self.old_heater == 0.0:
            if (self.T_heater >= ((self.min_temp*(self.G_heater+self.G_box)-self.G_box*self.room_temperature)/self.G_heater)
                                    *self.C_heater/(self.C_heater-self.step_size*self.G_heater)):
                self.heater_ctrl = False
            elif (self.T_heater <= (self.max_temp*(self.G_heater+self.G_box)-self.G_box*self.room_temperature)/self.G_heater 
                                    - self.V_heater*self.I_heater*self.step_size/self.C_heater):
                self.heater_ctrl = True
            else:
                # Failure state: we turn off the incubator for now
                self.heater_ctrl = False
                self._l.debug("Liveness Error")
        else:
            if (self.T_heater <= (self.max_temp*(self.G_heater+self.G_box)-self.G_box*self.room_temperature)/self.G_heater 
                                    - self.V_heater*self.I_heater*self.step_size/self.C_heater):
                self.heater_ctrl = True
            elif (self.T_heater >= ((self.min_temp*(self.G_heater+self.G_box)-self.G_box*self.room_temperature)/self.G_heater)
                                    *self.C_heater/(self.C_heater-self.step_size*self.G_heater)):
                self.heater_ctrl = False
            else:
                # Failure state: we turn off the incubator for now
                self.heater_ctrl = False
                self._l.debug("Liveness Error")
        

    def cleanup(self):
        self.safe_protocol()
        self.rabbitmq.close()

    def print_terminal(self, message):
        if not self.header_written:
            print("{:15}{:20}{:9}{:11}{:8}{:7}{:21}".format(
                "time", "execution_interval", "elapsed", "heater_on", "fan_on", "roomT", "box_air_temperature"
            ))
            self.header_written = True

        print("{:%d/%m %H:%M:%S}  {:<20.2f}{:<9.2f}{:11}{:8}{:<7.2f}{:<21.2f}".format(
            datetime.fromtimestamp(from_ns_to_s(message["time"])), message["fields"]["execution_interval"],
            message["fields"]["elapsed"],
            str(self.heater_ctrl), str(message["fields"]["fan_on"]), message["fields"]["t3"],
            self.box_air_temperature
        ))

    def upload_state(self, data):
        # Replaced the samples period and heating with the startup values in case something breaks
        ctrl_data = {
            "measurement": "controller",
            "time": time.time_ns(),
            "tags": {
                "source": "controller_safe"
            },
            "fields": {
                "plant_time": data["time"],
                "heater_on": self.heater_ctrl,
                "fan_on": data["fields"]["fan_on"],
                "current_state": "Heating" if self.heater_ctrl else "Cooling" ,
                "next_action_timer": 0,
                "n_samples_period": 40,
                "n_samples_heating": 5,
                "lower_bound": 35.0,
                "upper_bound": 40.0,
                "t_heater": self.T_heater
            }
        }
        self.rabbitmq.send_message(routing_key=ROUTING_KEY_CONTROLLER, message=ctrl_data)

    def control_loop_callback(self, ch, method, properties, body_json):
        self._record_message(body_json)

        self.kalman_prediction()
        self.ctrl_step()

        self.print_terminal(body_json)

        self.upload_state(body_json)

        assert self.heater_ctrl is not None
        self._set_heater_on(self.heater_ctrl)

    def update_parameters(self, ch, method, properties, body_json):
        self._l.debug("Request to update open loop controller parameters")

        n_samples_heating = body_json["n_samples_heating"]
        n_samples_period = body_json["n_samples_period"]
        self._l.debug(f"Updating open loop controller parameters to: {n_samples_heating, n_samples_period}")

        self.n_samples_period = n_samples_period
        self.n_samples_heating = n_samples_heating


    def start_control(self):
        try:
            self.rabbitmq.start_consuming()
        except:
            self._l.warning("Stopping controller")
            self.cleanup()
            raise
