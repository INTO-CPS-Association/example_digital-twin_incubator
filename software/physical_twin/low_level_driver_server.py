import logging
import time

import pika
from gpiozero import LED

# Import parameters and shared stuff
from communication.server.rabbitmq import Rabbitmq
from communication.shared.connection_parameters import *
from communication.shared.protocol import *
from physical_twin.sensor_actuator_layer import Heater, Fan, TemperatureSensor


class IncubatorDriver:
    HEAT_CTRL_QUEUE = "heater_control"
    FAN_CTRL_QUEUE = "fan_control"
    logger = logging.getLogger("Incubator")

    def __init__(self,
                 heater,
                 fan,
                 t1,
                 t2,
                 t3,
                 ip_raspberry=RASPBERRY_IP,
                 simulate_actuation=True
                 ):

        # Connection info
        self.rabbitmq = Rabbitmq(ip=ip_raspberry)

        # IO
        self.heater = heater
        self.fan = fan
        self.temperature_sensor = (t1, t2, t3)

        # Safety
        self.simulate_actuation = simulate_actuation

        # Always start in safe mode.
        self.actuators_off()

    def setup(self):
        self.rabbitmq.connect_to_server()
        self.logger.info("Connected.")
        self.rabbitmq.declare_queue(queue_name=self.FAN_CTRL_QUEUE,
                                    routing_key=ROUTING_KEY_FAN)
        self.rabbitmq.declare_queue(queue_name=self.HEAT_CTRL_QUEUE,
                                    routing_key=ROUTING_KEY_HEATER)

    def cleanup(self):
        self.logger.debug("Cleaning up.")
        self.actuators_off()
        self.rabbitmq.close()

    def actuators_off(self):
        self.fan.off()
        self.heater.off()

    def control_loop(self, exec_interval=3, strict_interval=True):
        try:
            while True:
                start = time.time()
                self.control_step(start, exec_interval)
                elapsed = time.time() - start
                if elapsed > exec_interval:
                    self.logger.error(
                        f"Control step taking {elapsed - exec_interval}s more than specified interval {exec_interval}s. Please specify higher interval.")
                    if strict_interval:
                        raise ValueError(exec_interval)
                else:
                    time.sleep(exec_interval - elapsed)
        except:
            self.cleanup()
            raise

    def control_step(self, start, exec_interval):
        self.react_control_signals()
        self.read_upload_state(start, exec_interval)

    def react_control_signals(self):
        heat_cmd = self._try_read_heat_control()
        fan_cmd = self._try_read_fan_control()

        if heat_cmd is not None:
            self.logger.debug(f"Heat command: on={heat_cmd}")
            self._safe_set_actuator(self.heater, heat_cmd)
        if fan_cmd is not None:
            self.logger.debug(f"Fan command: on={fan_cmd}")
            self._safe_set_actuator(self.fan, fan_cmd)

    def _safe_set_actuator(self, gpio_led: LED, on: bool):
        if on and gpio_led.is_lit:
            self.logger.debug(f"  Ignored command as it is already on.")
            return
        elif (not on) and (not gpio_led.is_lit):
            self.logger.debug(f"  Ignored command as it is already off.")
            return

        if on:
            if not self.simulate_actuation:
                gpio_led.on()
            else:
                self.logger.info("Pretending to set actuator on.")
        else:
            if not self.simulate_actuation:
                gpio_led.off()
            else:
                self.logger.info("Pretending to set actuator off.")

    def read_upload_state(self, start, exec_interval):
        n_sensors = len(self.temperature_sensor)
        readings = [] * n_sensors
        timestamps = [] * n_sensors
        for i in range(n_sensors):
            readings.append(self.temperature_sensor[i].read())
            timestamps.append(time.time())

        message = {
            "time": time.time(),
            "execution_interval": exec_interval,
            "heater_on": self.heater.is_lit,
            "fan_on": self.fan.is_lit
        }
        for i in range(n_sensors):
            message[f"t{i + 1}"] = readings[i]
            message[f"time_t{i + 1}"] = timestamps[i]

        message["elapsed"] = time.time() - start

        self.rabbitmq.send_message(ROUTING_KEY_STATE, message)
        self.logger.debug(f"Message sent to {ROUTING_KEY_STATE}.")
        self.logger.debug(message)

    def _try_read_heat_control(self):
        msg = self.rabbitmq.get_message(self.HEAT_CTRL_QUEUE)
        if msg is not None:
            return msg["heater"]
        else:
            return None

    def _try_read_fan_control(self):
        msg = self.rabbitmq.get_message(self.FAN_CTRL_QUEUE)
        if msg is not None:
            return msg["fan"]
        else:
            return None


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    incubator = IncubatorDriver(heater=Heater(12),
                                fan=Fan(13),
                                t1=TemperatureSensor("/sys/bus/w1/devices/10-0008039ad4ee/w1_slave"),
                                t2=TemperatureSensor("/sys/bus/w1/devices/10-0008039b25c1/w1_slave"),
                                t3=TemperatureSensor("/sys/bus/w1/devices/10-0008039a977a/w1_slave"),
                                simulate_actuation=False)
    incubator.setup()
    incubator.control_loop()
