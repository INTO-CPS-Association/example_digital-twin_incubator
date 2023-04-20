from incubator.config.config import config_logger, load_config
from mock_plant.mock_sensors_actuators import HeaterMock, LedMock, TemperatureSensorMock
from mock_plant.mock_connection import MOCK_TEMP_T1, MOCK_TEMP_T2, MOCK_TEMP_T3
from incubator.physical_twin.low_level_driver_server import IncubatorDriver, CTRL_EXEC_INTERVAL


def start_low_level_driver_mockup(ok_queue=None, exec_interval=CTRL_EXEC_INTERVAL):
    config_logger("logging.conf")
    config = load_config("startup.conf")

    incubator = IncubatorDriver(rabbit_config=config["rabbitmq"],
                                 heater=HeaterMock(config["rabbitmq"]),
                                 fan=LedMock(),
                                 t1=TemperatureSensorMock(MOCK_TEMP_T1, config["rabbitmq"]),
                                 t2=TemperatureSensorMock(MOCK_TEMP_T2, config["rabbitmq"]),
                                 t3=TemperatureSensorMock(MOCK_TEMP_T3, config["rabbitmq"]),
                                 simulate_actuation=False)
    incubator.setup()
    if ok_queue is not None:
        ok_queue.put("OK")
    incubator.control_loop(exec_interval)


if __name__ == '__main__':
    start_low_level_driver_mockup()

