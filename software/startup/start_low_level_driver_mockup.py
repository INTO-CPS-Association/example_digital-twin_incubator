import logging

from mock_plant.mock_sensors_actuators import HeaterMock, LedMock, TemperatureSensorMock
from startup.logging_config import config_logging
from mock_plant.mock_connection import MOCK_TEMP_T1, MOCK_TEMP_T2, MOCK_TEMP_T3
from physical_twin.low_level_driver_server import IncubatorDriver


if __name__ == '__main__':
    config_logging("ll_driver.log", level=logging.WARN)
    incubator = IncubatorDriver(ip_raspberry="localhost",
                                heater=HeaterMock(),
                                fan=LedMock(),
                                t1=TemperatureSensorMock(MOCK_TEMP_T1),
                                t2=TemperatureSensorMock(MOCK_TEMP_T2),
                                t3=TemperatureSensorMock(MOCK_TEMP_T3),
                                simulate_actuation=False)
    incubator.setup()
    incubator.control_loop()
