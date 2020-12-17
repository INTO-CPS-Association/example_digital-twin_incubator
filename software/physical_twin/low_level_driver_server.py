import logging
import sys
import time

import pika
import json
import datetime
from gpiozero import LED
from pika import BlockingConnection
import temperature_sensor

# Import parameters and shared stuff
# sys.path.append("../communication/shared")
from communication.shared.connection_parameters import *
from communication.shared.protocol import *


def _convert_str_to_bool(body):
    if body is None:
        return None
    else:
        return body.decode(ENCODING) == "True"


class IncubatorDriver:
    HEAT_CTRL_QUEUE = "heater_control"
    FAN_CTRL_QUEUE = "fan_control"
    logger = logging.getLogger("Incubator")

    def __init__(self, ip_raspberry=RASPBERRY_IP,
                 port=RASPBERRY_PORT,
                 username=PIKA_USERNAME,
                 password=PIKA_PASSWORD,
                 vhost=PIKA_VHOST,
                 exchange_name=PIKA_EXCHANGE,
                 exchange_type=PIKA_EXCHANGE_TYPE,
                 heater_pin=12,
                 fan_pin=13,
                 simulate_actuation=True
                 ):

        # Connection info
        self.vhost = vhost
        self.exchange_name = exchange_name
        self.exchange_type = exchange_type

        credentials = pika.PlainCredentials(username, password)
        self.parameters = pika.ConnectionParameters(ip_raspberry,
                                                    port,
                                                    vhost,
                                                    credentials)
        self.connection = None
        self.channel = None

        # IO
        self.heater = LED(heater_pin)
        self.fan = LED(fan_pin)
        self.temperature_sensor = ("/sys/bus/w1/devices/10-0008039ad4ee/w1_slave",
                                   "/sys/bus/w1/devices/10-0008039b25c1/w1_slave",
                                   "/sys/bus/w1/devices/10-0008039a977a/w1_slave")

        # Safety
        self.simulate_actuation = simulate_actuation

        # Always start in safe mode.
        self.actuators_off()

    def setup(self):
        self.connection = pika.BlockingConnection(self.parameters)
        self.logger.info("Connected.")
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange=self.exchange_name, exchange_type=self.exchange_type)

        # TODO: Make these routing keys global between client and server
        self.declare_queue(queue_name=self.FAN_CTRL_QUEUE,
                           routing_key=ROUTING_KEY_FAN)
        self.declare_queue(queue_name=self.HEAT_CTRL_QUEUE,
                           routing_key=ROUTING_KEY_HEATER)

    def cleanup(self):
        self.logger.debug("Cleaning up.")
        self.actuators_off()
        self.channel.queue_unbind(queue=FAN_CTRL_QUEUE, exchange=self.exchange_name)
        self.channel.queue_delete(queue=FAN_CTRL_QUEUE)
        self.channel.queue_unbind(queue=HEAT_CTRL_QUEUE, exchange=self.exchange_name)
        self.channel.queue_delete(queue=HEAT_CTRL_QUEUE)
        self.channel.close()
        self.connection.close()

    def actuators_off(self):
        self.fan.off()
        self.heater.off()

    def declare_queue(self, queue_name, routing_key):
        self.channel.queue_declare(queue_name, exclusive=True)
        self.channel.queue_bind(
            exchange=self.exchange_name,
            queue=queue_name,
            routing_key=routing_key
        )
        self.logger.info(f"Bound {routing_key}--> {queue_name}")

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
        readings = []*n_sensors
        timestamps = []*n_sensors
        for i in range(n_sensors):
            readings.append(temperature_sensor.read_sensor(self.temperature_sensor[i]))
            timestamps.append(time.time())

        message = {
            "time": time.time(),
            "execution_interval": exec_interval,
            "heater_on": self.heater.is_lit,
            "fan_on": self.fan.is_lit
        }
        for i in range(n_sensors):
            message[f"t{i+1}"] = readings[i]
            message[f"time_t{i+1}"] = timestamps[i]

        message["elapsed"] = time.time() - start

        self.channel.basic_publish(
            exchange=PIKA_EXCHANGE, routing_key=ROUTING_KEY_STATE, body=json.dumps(message))
        self.logger.debug(f"Message sent to {ROUTING_KEY_STATE}.")
        self.logger.debug(message)

    def _log_message(self, queue_name, method, properties, body):
        self.logger.debug(f"Message received in queue {queue_name}.")
        self.logger.debug(f"  method={method}")
        self.logger.debug(f"  properties={properties}")
        self.logger.debug(f"  body={body}")

    def _try_read_heat_control(self):
        (method, properties, body) = incubator.channel.basic_get(self.HEAT_CTRL_QUEUE, auto_ack=True)
        self._log_message(self.HEAT_CTRL_QUEUE, method, properties, body)
        return _convert_str_to_bool(body)

    def _try_read_fan_control(self):
        (method, properties, body) = incubator.channel.basic_get(self.FAN_CTRL_QUEUE, auto_ack=True)
        self._log_message(self.FAN_CTRL_QUEUE, method, properties, body)
        return _convert_str_to_bool(body)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    incubator = IncubatorDriver()
    incubator.setup()
    incubator.control_loop()
