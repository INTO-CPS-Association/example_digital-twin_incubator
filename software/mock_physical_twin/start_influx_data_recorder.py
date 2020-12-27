import logging

from digital_twin.data_access.dbmanager.incubator_state_influx_recorder import IncubatorDataRecorderInflux

if __name__ == '__main__':
    # noinspection PyArgumentList
    logging.basicConfig(level=logging.DEBUG,
                        handlers=[
                            logging.FileHandler("influx_data_recorder.log"),
                            logging.StreamHandler()
                        ],
                        format='%(asctime)s.%(msecs)03d %(name)s %(levelname)s %(module)s - %(funcName)s: %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S'
                        )
    recorder = IncubatorDataRecorderInflux()
    recorder.start_recording(rabbitmq_ip="localhost")
