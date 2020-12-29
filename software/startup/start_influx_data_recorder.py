import logging

from digital_twin.data_access.dbmanager.incubator_state_influx_recorder import IncubatorDataRecorderInflux
from startup.logging_config import config_logging

if __name__ == '__main__':
    config_logging("influx_data_recorder.log", level=logging.WARN)
    recorder = IncubatorDataRecorderInflux()
    recorder.start_recording(rabbitmq_ip="localhost")
