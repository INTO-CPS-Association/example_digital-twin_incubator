from incubator.config.config import config_logger, load_config
from digital_twin.data_access.dbmanager.incubator_state_csv_recorder import IncubatorDataRecorderCSV

if __name__ == '__main__':
    config_logger("logging.conf")
    config = load_config("startup.conf")
    recorder = IncubatorDataRecorderCSV(csv_file_path=".", csv_file_prefix="mock", rollover_limit=10000)
    recorder.start_recording(rabbit_config=config["rabbitmq"])
