"""
These classes form a layer that decouples the low level driver from the hardware.
This way we can test the low level driver ussing a local setup with rabbit mq, without having an actual incubator.
"""

from gpiozero import LED
import re
import time
import adafruit_dht
import board
import mh_z19


class Heater(LED):
    def __init__(self, pin=None):
        super(Heater, self).__init__(pin=pin)


class Fan(LED):
    def __init__(self, pin=None):
        super(Fan, self).__init__(pin=pin)

class Pump(LED):
    def __init__(self, pin=None):
        super(Pump, self).__init__(pin=pin)

class CO2Sensor:
    def read(self):
        return mh_z19.read()

class HumiditySensor:
    def __init__(self, path=None):
        pin = getattr(board, f"D{path}") # Hack to convert pin number to adafruit board class
        self.device = adafruit_dht.DHT22(pin)
    
    def read(self):
        try:
            humidity = self.device.humidity
        except Exception as e:
            print(e)
            humidity = -1.0
        return humidity


class TemperatureSensor:
    def __init__(self, path=None):
        self.path = path

    def read(self):
        """
        read and parse sensor data file
        :return:
        """
        value = "U"
        try:
            f = open(self.path, "r")
            line = f.readline()
            if re.match(r"([0-9a-f]{2} ){9}: crc=[0-9a-f]{2} YES", line):
                line = f.readline()
                m = re.match(r"([0-9a-f]{2} ){9}t=([+-]?[0-9]+)", line)
                if m:
                    value = str(float(m.group(2)) / 1000.0)
            f.close()
        except IOError as e:
            print(time.strftime("%x %X"), "Error reading", self.path, ": ", e)
            raise e
        return value