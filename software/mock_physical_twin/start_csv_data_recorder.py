import logging

from digital_twin.data_access.dbmanager.incubator_state_csv_recorder import IncubatorDataRecorderCSV

if __name__ == '__main__':
    logging.basicConfig(level=logging.WARN,
                        handlers=[
                            logging.FileHandler("csv_data_recorder.log"),
                            logging.StreamHandler()
                        ],
                        format='%(asctime)s.%(msecs)03d %(name)s %(levelname)s %(module)s - %(funcName)s: %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S'
                        )
    recorder = IncubatorDataRecorderCSV(csv_file_path=".", csv_file_prefix="mock", rollover_limit=10000)
    recorder.start_recording(rabbitmq_ip="localhost")
