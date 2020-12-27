import time
import sys
from datetime import datetime
import logging

from communication.server.rabbitmq import Rabbitmq, ROUTING_KEY_STATE, ROUTING_KEY_HEATER, ROUTING_KEY_FAN, decode_json, \
    from_ns_to_s, ROUTING_KEY_CONTROLLER
from communication.shared.connection_parameters import RASPBERRY_IP

LINE_PRINT_FORMAT = {
    "time": "{:20}",
    "execution_interval": "{:<2.1f}",
    "elapsed": "{:<2.1f}",
    "heater_on": "{:10}",
    "fan_on": "{:10}",
    "t1": "{:<6.2f}",
    "box_air_temperature": "{:<15.2f}",
    "state": "{:6}"
}


class ControllerPhysical():
    def __init__(self, rabbitmq_ip=RASPBERRY_IP, desired_temperature=35.0, lower_bound=5, heating_time=20,
                 heating_gap=30):
        self.desired_temperature = desired_temperature
        self.lower_bound = lower_bound
        self.heating_time = heating_time
        self.heating_gap = heating_gap

        self._l = logging.getLogger("ControllerPhysical")

        self.box_air_temperature = None
        self.room_temperature = None

        self.heater_ctrl = None
        self.current_state = "CoolingDown"
        self.next_time = -1.0

        self.rabbitmq = Rabbitmq(ip=rabbitmq_ip)
        self.state_queue_name = 'state'

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

    def ctrl_step(self):
        if self.box_air_temperature >= 58:
            self._l.error("Temperature exceeds 58, Cleaning up.")
            self.cleanup()
            sys.exit(0)

        if self.current_state == "CoolingDown":
            self._l.debug("current state is: CoolingDown")
            self.heater_ctrl = False
            if self.box_air_temperature <= self.desired_temperature - self.lower_bound:
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
                if self.box_air_temperature <= self.desired_temperature:
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
            print("{:13}{:20}{:9}{:11}{:8}{:7}{:21}{:6}".format(
                "time", "execution_interval", "elapsed", "heater_on", "fan_on", "t1", "box_air_temperature", "state"
            ))
            self.header_written = True

        print("{:%d/%m %H:%M}  {:<20.2f}{:<9.2f}{:11}{:8}{:<7.2f}{:<21.2f}{:6}".format(
            datetime.fromtimestamp(from_ns_to_s(message["time"])), message["fields"]["execution_interval"], message["fields"]["elapsed"],
            str(self.heater_ctrl), str(message["fields"]["fan_on"]), message["fields"]["t1"],
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
                "temperature_desired": self.desired_temperature,
                "lower_bound": self.lower_bound,
                "heating_time": self.heating_time,
                "heating_gap": self.heating_gap,
            }
        }
        self.rabbitmq.send_message(routing_key=ROUTING_KEY_CONTROLLER, message=ctrl_data)

    def control_loop_callback(self, ch, method, properties, body):

        message = decode_json(body)
        self._record_message(message)

        self.ctrl_step()

        self.print_terminal(message)

        self.upload_state(message)

        assert self.heater_ctrl is not None
        self._set_heater_on(self.heater_ctrl)

    def start_control(self):
        try:
            self.setup()
            self.rabbitmq.subscribe(queue_name=self.state_queue_name,
                                    routing_key=ROUTING_KEY_STATE,
                                    on_message_callback=self.control_loop_callback)
            self.rabbitmq.start_consuming()
        except:
            self._l.warning("Stopping controller")
            self.cleanup()
            raise




if __name__ == '__main__':
    desired_temperature = float(input("Please input desired temperature: "))
    controller = ControllerPhysical(desired_temperature=desired_temperature)
    controller.start_control()
