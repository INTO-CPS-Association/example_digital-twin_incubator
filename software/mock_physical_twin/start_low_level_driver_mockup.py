import logging

from communication.server.rabbitmq import Rabbitmq
from mock_physical_twin.mock_connection import MOCK_HEATER_ON, MOCK_TEMP_T1, MOCK_TEMP_T2, MOCK_TEMP_T3
from physical_twin.low_level_driver_server import IncubatorDriver


class LedMock:
    def __init__(self):
        self.is_lit = False

    def off(self):
        self.is_lit = False

    def on(self):
        self.is_lit = True


class HeaterMock(LedMock):
    def __init__(self, ip_rabbitmq="localhost"):
        super(HeaterMock, self).__init__()
        self.comm = Rabbitmq(ip_raspberry=ip_rabbitmq)
        self.comm.connect_to_server()

        self.state_on = False

    def off(self):
        super(HeaterMock, self).off()
        self.comm.send_message(MOCK_HEATER_ON, {"heater": False})

    def on(self):
        super(HeaterMock, self).on()
        self.comm.send_message(MOCK_HEATER_ON, {"heater": True})


class TemperatureSensorMock:
    def __init__(self, temp_key, ip_rabbitmq="localhost"):
        self.comm = Rabbitmq(ip_raspberry=ip_rabbitmq)
        self.key = temp_key
        self.comm.connect_to_server()
        self.comm.declare_queue(queue_name=self.key, routing_key=self.key)
        self.cached_temp = 20.0

    def read(self):
        reading = self.comm.get_message(queue_name=self.key)
        if reading is not None:
            self.cached_temp = reading
        return self.cached_temp


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    incubator = IncubatorDriver(ip_raspberry="localhost",
                                heater=HeaterMock(),
                                fan=LedMock(),
                                t1=TemperatureSensorMock(MOCK_TEMP_T1),
                                t2=TemperatureSensorMock(MOCK_TEMP_T2),
                                t3=TemperatureSensorMock(MOCK_TEMP_T3),
                                simulate_actuation=False)
    incubator.setup()
    incubator.control_loop()
