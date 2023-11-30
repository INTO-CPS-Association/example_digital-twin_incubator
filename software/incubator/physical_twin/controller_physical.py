import time
import sys
from datetime import datetime
import logging

from incubator.communication.server.rabbitmq import Rabbitmq, ROUTING_KEY_STATE, ROUTING_KEY_HEATER, ROUTING_KEY_FAN, \
    from_ns_to_s, ROUTING_KEY_CONTROLLER
from incubator.communication.shared.protocol import ROUTING_KEY_UPDATE_CLOSED_CTRL_PARAMS
from incubator.models.controller_models.controller_model_sm import ControllerModel4SM


class ControllerPhysical:
    def __init__(self, rabbit_config, temperature_desired=35.0, lower_bound=5.0, heating_time=20.0,
                 heating_gap=30.0):
        self._l = logging.getLogger("ControllerPhysical")

        self.box_air_temperature = None
        self.room_temperature = None

        self.heater_ctrl = None
        self.fan_ctrl = None
        self.state_machine = ControllerModel4SM(temperature_desired, lower_bound, heating_time, heating_gap)

        self.rabbitmq = Rabbitmq(**rabbit_config)

        self.header_written = False

    def _record_message(self, message):
        sensor_room = message['fields']['t3']
        self.box_air_temperature = message['fields']['average_temperature']
        self.room_temperature = sensor_room
    
    def safe_protocol(self):
        self._l.debug("Stopping Fan")
        self.fan_ctrl = False
        self._set_fan_on(False)
        self._l.debug("Stopping Heater")
        self.heater_ctrl = False
        self._set_heater_on(False)

    def _set_heater_on(self, on):
        self.rabbitmq.send_message(routing_key=ROUTING_KEY_HEATER, message={"heater": on})

    def _set_fan_on(self, on):
        self.fan_ctrl = on
        self.rabbitmq.send_message(routing_key=ROUTING_KEY_FAN, message={"fan": on})

    def setup(self):
        self.rabbitmq.connect_to_server()
        self.safe_protocol()
        self.rabbitmq.subscribe(routing_key=ROUTING_KEY_UPDATE_CLOSED_CTRL_PARAMS,
                                on_message_callback=self.update_parameters)
        self.rabbitmq.subscribe(routing_key=ROUTING_KEY_STATE,
                                on_message_callback=self.control_loop_callback)

    def ctrl_step(self):
        if self.box_air_temperature >= 58:
            self._l.error("Temperature exceeds 58, Cleaning up.")
            self.cleanup()
            sys.exit(1)

        self.fan_ctrl = True
        self.state_machine.step(time.time(), self.box_air_temperature)
        self.heater_ctrl = self.state_machine.cached_heater_on

    def cleanup(self):
        self.safe_protocol()
        self.rabbitmq.close()

    def print_terminal(self, message):
        if not self.header_written:
            print("{:16}{:15}{:9}{:11}{:8}{:7}{:21}{:6}".format(
                "time", "exec_interval", "elapsed", "heater_on", "fan_on", "room", "box_air_temperature", "state"
            ))
            self.header_written = True

        print("{:%d/%m %H:%M:%S}  {:<15.2f}{:<9.2f}{:11}{:8}{:<7.2f}{:<21.2f}{:6}".format(
            datetime.fromtimestamp(from_ns_to_s(message["time"])), message["fields"]["execution_interval"],
            message["fields"]["elapsed"],
            str(self.heater_ctrl), str(message["fields"]["fan_on"]), self.room_temperature,
            self.box_air_temperature, self.state_machine.current_state
        ))

    def upload_state(self, data):
        ctrl_data = {
            "measurement": "controller",
            "time": time.time_ns(),
            "tags": {
                "source": "controller"
            },
            "fields": {
                "plant_time": data["time"],
                "heater_on": self.heater_ctrl,
                "fan_on": data["fields"]["fan_on"],
                "current_state": self.state_machine.current_state,
                "next_time": self.state_machine.next_time,
                "temperature_desired": self.state_machine.temperature_desired,
                "lower_bound": self.state_machine.lower_bound,
                "heating_time": self.state_machine.heating_time,
                "heating_gap": self.state_machine.heating_gap,
            }
        }
        self.rabbitmq.send_message(routing_key=ROUTING_KEY_CONTROLLER, message=ctrl_data)

    def _safe_update_parameter(self, data, data_key, parameter, type_convert, value_check):
        assert hasattr(self.state_machine, parameter)
        if data_key in data:
            new_val = type_convert(data[data_key])
            if value_check(new_val):
                self._l.debug(f"Updating {parameter} to {new_val}.")
                setattr(self.state_machine, parameter, new_val)
            else:
                self._l.warning(f"Update of {parameter} to {new_val} failed. Invalid value.")

    def update_parameters(self, ch, method, properties, body_json):
        self._l.debug("New parameter msg:")
        self._l.debug(body_json)
        self._safe_update_parameter(body_json, 'temperature_desired', 'temperature_desired', float, lambda v: v < 45)

    def control_loop_callback(self, ch, method, properties, body_json):
        self._record_message(body_json)

        self.ctrl_step()

        self.print_terminal(body_json)

        self.upload_state(body_json)

        assert self.heater_ctrl is not None
        self._set_heater_on(self.heater_ctrl)
        self._set_fan_on(self.fan_ctrl)

    def start_control(self):
        try:
            self.rabbitmq.start_consuming()
        except:
            self._l.warning("Stopping controller")
            self.cleanup()
            raise



