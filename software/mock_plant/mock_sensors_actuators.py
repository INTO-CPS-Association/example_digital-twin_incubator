from communication.server.rabbitmq import Rabbitmq
from mock_plant.mock_connection import MOCK_HEATER_ON


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
        self.ip = ip_rabbitmq

        self.state_on = False

    def off(self):
        super(HeaterMock, self).off()
        # Open a new connections everytime because this method is not called very often.
        with Rabbitmq(ip=self.ip) as con:
            con.send_message(MOCK_HEATER_ON, {"heater": False})

    def on(self):
        super(HeaterMock, self).on()
        # Open a new connections everytime because this method is not called very often.
        with Rabbitmq(ip=self.ip) as con:
            con.send_message(MOCK_HEATER_ON, {"heater": True})


class TemperatureSensorMock:
    def __init__(self, temp_key, ip_rabbitmq="localhost"):
        self.comm = Rabbitmq(ip=ip_rabbitmq)
        self.key = temp_key
        self.comm.connect_to_server()
        self.queue_name = self.comm.declare_local_queue(routing_key=self.key)
        self.cached_temp = 20.0

    def read(self):
        reading = self.comm.get_message(queue_name=self.queue_name)
        if reading is not None:
            self.cached_temp = reading
        return self.cached_temp

