import logging

from digital_twin.data_access.dbmanager.incubator_state_csv_recorder import IncubatorDataRecorderCSV
from startup.utils.logging_config import config_logging

if __name__ == '__main__':
    config_logging("logs/csv_data_recorder.log", level=logging.WARN)
    recorder = IncubatorDataRecorderCSV(csv_file_path=".", csv_file_prefix="mock", rollover_limit=10000)
    recorder.start_recording(rabbitmq_ip="10.17.98.239")
