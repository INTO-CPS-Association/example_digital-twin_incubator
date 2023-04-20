import time
import sys
from datetime import datetime
import logging

from communication.server.rabbitmq import Rabbitmq, ROUTING_KEY_STATE, ROUTING_KEY_HEATER, ROUTING_KEY_FAN, decode_json, \
    from_ns_to_s, ROUTING_KEY_CONTROLLER
from communication.shared.protocol import ROUTING_KEY_COSIM_PARAM

class ControllerPhysical:
    def __init__(self, rabbit_config, temperature_desired=35.0, lower_bound=5.0, heating_time=20.0,
                 heating_gap=30.0):
        self.temperature_desired = temperature_desired
        self.lower_bound = lower_bound
        self.heating_time = heating_time
        self.heating_gap = heating_gap

        self._l = logging.getLogger("ControllerPhysical")

        self.box_air_temperature = None
        self.room_temperature = None

        self.heater_ctrl = None
        self.current_state = "CoolingDown"
        self.next_time = -1.0

        self.rabbitmq = Rabbitmq(**rabbit_config)

        self.header_written = False

    def _record_message(self, message):
        sensor_room = message['fields']['t3']
        self.box_air_temperature = message['fields']['average_temperature']
        self.room_temperature = sensor_room

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
        self.rabbitmq.subscribe(routing_key=ROUTING_KEY_COSIM_PARAM,
                                on_message_callback=self.update_parameters)
        self.rabbitmq.subscribe(routing_key=ROUTING_KEY_STATE,
                                on_message_callback=self.control_loop_callback)

    def ctrl_step(self):
        if self.box_air_temperature >= 58:
            self._l.error("Temperature exceeds 58, Cleaning up.")
            self.cleanup()
            sys.exit(0)

        if self.current_state == "CoolingDown":
            self._l.debug("current state is: CoolingDown")
            self.heater_ctrl = False
            if self.box_air_temperature <= self.temperature_desired - self.lower_bound:
                self.current_state = "Heating"
                self.heater_ctrl = True
                self.next_time = time.time() + self.heating_time
                return
        if self.current_state == "Heating":
            self._l.debug("current state is: Heating")
            self.heater_ctrl = True
            if 0 < self.next_time <= time.time():
                self.current_state = "Waiting"
                self.heater_ctrl = False
                self.next_time = time.time() + self.heating_gap
            return
        if self.current_state == "Waiting":
            self._l.debug("current state is: Waiting")
            self.heater_ctrl = False
            if 0 < self.next_time <= time.time():
                if self.box_air_temperature <= self.temperature_desired and self.heating_time > 0:
                    self.current_state = "Heating"
                    self.heater_ctrl = True
                    self.next_time = time.time() + self.heating_time
                else:
                    self.current_state = "CoolingDown"
                    self.heater_ctrl = False
                    self.next_time = -1.0
            return

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
            self.box_air_temperature, self.current_state
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
                "current_state": self.current_state,
                "next_time": self.next_time,
                "temperature_desired": self.temperature_desired,
                "lower_bound": self.lower_bound,
                "heating_time": self.heating_time,
                "heating_gap": self.heating_gap,
            }
        }
        self.rabbitmq.send_message(routing_key=ROUTING_KEY_CONTROLLER, message=ctrl_data)

    def _safe_update_parameter(self, data, data_key, parameter, type_convert, value_check):
        assert hasattr(self, parameter)
        if data_key in data:
            new_val = type_convert(data[data_key])
            if value_check(new_val):
                self._l.debug(f"Updating {parameter} to {new_val}.")
                setattr(self, parameter, new_val)
            else:
                self._l.warning(f"Update of {parameter} to {new_val} failed. Invalid value.")

    def update_parameters(self, ch, method, properties, body_json):
        self._l.debug("New parameter msg:")
        self._l.debug(body_json)
        # TODO Ensure message is safe, then change parameters of the controller.
        self._safe_update_parameter(body_json, 'C_in', 'heating_gap', float, lambda v: 0 < v)
        # 100 is the hardcoded max heating time. for safety reasons
        self._safe_update_parameter(body_json, 'H_in', 'heating_time', float, lambda v: v < 100)
        self._safe_update_parameter(body_json, 'LL_in', 'lower_bound', float, lambda v: 0 < v)

    def control_loop_callback(self, ch, method, properties, body_json):
        self._record_message(body_json)

        self.ctrl_step()

        self.print_terminal(body_json)

        self.upload_state(body_json)

        assert self.heater_ctrl is not None
        self._set_heater_on(self.heater_ctrl)

    def start_control(self):
        try:
            self.rabbitmq.start_consuming()
        except:
            self._l.warning("Stopping controller")
            self.cleanup()
            raise

