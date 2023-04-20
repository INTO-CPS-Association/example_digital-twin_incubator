import time
import sys
from datetime import datetime
import logging

from communication.server.rabbitmq import Rabbitmq, ROUTING_KEY_STATE, ROUTING_KEY_HEATER, ROUTING_KEY_FAN, decode_json, \
    from_ns_to_s, ROUTING_KEY_CONTROLLER
from communication.shared.protocol import ROUTING_KEY_UPDATE_CTRL_PARAMS
from models.controller_models.controller_open_loop import ControllerOpenLoopSM

class ControllerPhysicalOpenLoop:
    def __init__(self, rabbit_config,
                 n_samples_period,  # Total number of samples considered
                 n_samples_heating,  # Number of samples (out of n_samples_period) that the heater is on.
                 ):
        self._l = logging.getLogger("OpenLoopControllerPhysical")

        self.box_air_temperature = None
        self.room_temperature = None
        self.heater_ctrl = None

        self.n_samples_period = n_samples_period
        self.n_samples_heating = n_samples_heating
        self.state_machine = ControllerOpenLoopSM(n_samples_period, n_samples_heating)

        self.rabbitmq = Rabbitmq(**rabbit_config)

        self.header_written = False

    def _record_message(self, message):
        sensor1_reading = message['fields']['t1']
        self.box_air_temperature = message['fields']['average_temperature']
        self.room_temperature = sensor1_reading

    def safe_protocol(self):
        self._l.debug("Stopping Fan")
        self._set_fan_on(False)
        self._l.debug("Stopping Heater")
        self._set_heater_on(False)

    def _set_heater_on(self, on):
        self.rabbitmq.send_message(routing_key=ROUTING_KEY_HEATER, message={"heater": on})

    def _set_fan_on(self, on):
        self.rabbitmq.send_message(routing_key=ROUTING_KEY_FAN, message={"fan": on})

    def setup(self):
        self.rabbitmq.connect_to_server()
        self.safe_protocol()
        self._l.debug("Starting Fan")
        self._set_fan_on(True)
        self.rabbitmq.subscribe(routing_key=ROUTING_KEY_UPDATE_CTRL_PARAMS,
                                on_message_callback=self.update_parameters)
        self.rabbitmq.subscribe(routing_key=ROUTING_KEY_STATE,
                                on_message_callback=self.control_loop_callback)

    def ctrl_step(self):
        self.state_machine.step()
        self.heater_ctrl = self.state_machine.cached_heater_on

    def cleanup(self):
        self.safe_protocol()
        self.rabbitmq.close()

    def print_terminal(self, message):
        if not self.header_written:
            print("{:15}{:20}{:9}{:11}{:8}{:7}{:21}{:6}".format(
                "time", "execution_interval", "elapsed", "heater_on", "fan_on", "t1", "box_air_temperature", "state"
            ))
            self.header_written = True

        print("{:%d/%m %H:%M:%S}  {:<20.2f}{:<9.2f}{:11}{:8}{:<7.2f}{:<21.2f}{:6}".format(
            datetime.fromtimestamp(from_ns_to_s(message["time"])), message["fields"]["execution_interval"],
            message["fields"]["elapsed"],
            str(self.heater_ctrl), str(message["fields"]["fan_on"]), message["fields"]["t1"],
            self.box_air_temperature, self.state_machine.current_state
        ))

    def upload_state(self, data):
        ctrl_data = {
            "measurement": "controller",
            "time": time.time_ns(),
            "tags": {
                "source": "controller_open_loop"
            },
            "fields": {
                "plant_time": data["time"],
                "heater_on": self.heater_ctrl,
                "fan_on": data["fields"]["fan_on"],
                "current_state": self.state_machine.current_state,
                "next_action_timer": self.state_machine.next_action_timer,
                "n_samples_period": self.n_samples_period,
                "n_samples_heating": self.n_samples_heating,
            }
        }
        self.rabbitmq.send_message(routing_key=ROUTING_KEY_CONTROLLER, message=ctrl_data)

    def control_loop_callback(self, ch, method, properties, body_json):
        self._record_message(body_json)

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
        self.state_machine = ControllerOpenLoopSM(n_samples_period, n_samples_heating)

    def start_control(self):
        try:
            self.rabbitmq.start_consuming()
        except:
            self._l.warning("Stopping controller")
            self.cleanup()
            raise
