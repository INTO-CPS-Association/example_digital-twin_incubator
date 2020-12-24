import time
import sys
from datetime import datetime

try:
    from communication.shared.connection_parameters import *
    from communication.shared.protocol import *
    from communication.server.rabbitmq import Rabbitmq
except:
    raise

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
        self.temperature_desired = desired_temperature
        self.lower_bound = lower_bound
        self.heating_time = heating_time
        self.heating_gap = heating_gap

        self.box_air_temperature = None
        self.room_temperature = None

        self.heater_ctrl = None
        self.current_state = "CoolingDown"
        self.next_time = -1.0

        self.rabbitmq = Rabbitmq(ip_raspberry=rabbitmq_ip)
        self.state_queue_name = 'state'
        self.message = None

        self.header_written = False

        print("Before running actually, please make sure that the low_level_deriver_server is running")

    def _record_message(self, message):
        sensor1_reading = message['t1']
        sensor2_reading = message['t2']
        sensor3_reading = message['t3']
        self.box_air_temperature = (sensor2_reading + sensor3_reading) / 2
        self.room_temperature = sensor1_reading

    def safe_protocol(self):
        print("Closing Fan")
        self._set_fan_on(False)
        print("Closing Heater")
        self._set_heater_on(False)

    # this can be further used to self-adaption
    def change_controller_parameters(self, desired_temperature_=35.0, lower_bound=5, heating_time=0.2, heating_gap=0.3):
        self.temperature_desired = desired_temperature_
        self.lower_bound = lower_bound
        self.heating_time = heating_time
        self.heating_gap = heating_gap
        print(f"Controller parameters have been changed to"
              f"\ntemperature_desired:{self.temperature_desired}"
              f"\nlower_bound:{self.lower_bound}"
              f"\nheating_time:{self.heating_time}"
              f"\nheating_gap:{self.heating_gap}"
              )

    def _set_heater_on(self, on):
        self.rabbitmq.send_message(routing_key=ROUTING_KEY_HEATER, message={"heater": on})

    def _set_fan_on(self, on):
        self.rabbitmq.send_message(routing_key=ROUTING_KEY_FAN, message={"fan": on})

    def setup(self):
        self.rabbitmq.connect_to_server()
        self.rabbitmq.declare_queue(queue_name=self.state_queue_name, routing_key=ROUTING_KEY_STATE)
        self.safe_protocol()
        self._set_fan_on(True)

    def ctrl_step(self):
        if self.box_air_temperature >= 58:
            print("Temperature exceeds 58, Cleaning up")
            self.cleanup()
            sys.exit(0)

        if self.current_state == "CoolingDown":
            # print("current state is: CoolingDown")
            self.heater_ctrl = False
            if self.box_air_temperature <= self.temperature_desired - self.lower_bound:
                self.current_state = "Heating"
                self.heater_ctrl = True
                self.next_time = time.time() + self.heating_time
                return
        if self.current_state == "Heating":
            # print("current state is: Heating")
            self.heater_ctrl = True
            if 0 < self.next_time <= time.time():
                self.current_state = "Waiting"
                self.heater_ctrl = False
                self.next_time = time.time() + self.heating_gap
            return
        if self.current_state == "Waiting":
            # print("current state is: Waiting")
            self.heater_ctrl = False
            if 0 < self.next_time <= time.time():
                if self.box_air_temperature <= self.temperature_desired:
                    self.current_state = "Heating"
                    self.heater_ctrl = True
                    self.next_time = time.time() + self.heating_time
                else:
                    self.current_state = "CoolingDown"
                    self.heater_ctrl = False
                    self.next_time = -1
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
            datetime.fromtimestamp(message["time"]), message["execution_interval"], message["elapsed"],
            str(message["heater_on"]), str(message["fan_on"]), message["t1"],
            self.box_air_temperature, self.current_state
        ))

    def control_loop_callback(self, ch, method, properties, body):

        message = decode_json(body)
        self._record_message(message)

        self.ctrl_step()

        self.print_terminal(message)

        assert self.heater_ctrl is not None
        self._set_heater_on(self.heater_ctrl)

    def start_control(self):
        try:
            self.setup()
            self.rabbitmq.channel.basic_consume(queue=self.state_queue_name,
                                                on_message_callback=self.control_loop_callback,
                                                auto_ack=True
                                                )
            self.rabbitmq.channel.start_consuming()
        except:
            print("Cleaning Process")
            self.cleanup()
            raise


if __name__ == '__main__':
    desired_temperature = float(input("Please input desired temperature: "))
    controller = ControllerPhysical(desired_temperature=desired_temperature)
    controller.start_control()
