import logging

from digital_twin.data_access.data_recorder import IncubatorDataRecorder
from physical_twin.controller_physical import ControllerPhysical

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    recorder = IncubatorDataRecorder(csv_file_path=".", csv_file_prefix="mock", rollover_limit=10000)
    recorder.start_recording(rabbitmq_ip="localhost")
