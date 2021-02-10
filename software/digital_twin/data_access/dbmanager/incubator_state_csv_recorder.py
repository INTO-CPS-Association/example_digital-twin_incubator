"""
Contains the implementation of the component that is responsible for storing the data from the incubator.
"""
import csv
import logging
import os
from datetime import datetime

from incubator.communication.server.rabbitmq import Rabbitmq
from incubator.communication.shared.protocol import ROUTING_KEY_STATE


class IncubatorDataRecorderCSV():
    def __init__(self, csv_file_path, csv_file_prefix, rollover_limit):
        self._l = logging.getLogger("IncubatorDataRecorder")
        self.csv_file_path = csv_file_path
        self.csv_file_prefix = csv_file_prefix
        self.rollover_limit = rollover_limit

        self.current_file_name = None
        self.number_records = 0
        self.header_written = False
        self.current_file = None
        self.csv_writer = None

    def read_state(self, ch, method, properties, body_json):
        self._l.debug("New msg:")
        self._l.debug(body_json)

        if self.current_file_name is None or self.number_records >= self.rollover_limit:
            if self.current_file_name is not None:
                self.current_file.close()

            self.current_file_name = datetime.now().strftime(f"{self.csv_file_prefix}_%Y-%m-%d__%H_%M_%S.csv")
            new_dir = os.path.join(self.csv_file_path, self.current_file_name)
            self._l.debug(f"Rollover to new file in {new_dir}.")
            self.current_file = open(new_dir, 'w', newline='')
            self.csv_writer = csv.writer(self.current_file)
            self.number_records = 0
            self.header_written = False

        if not self.header_written:
            self._l.debug("Writing header.")
            header = ["time"]
            header += list(body_json["fields"].keys())
            self.csv_writer.writerow(header)
            self.header_written = True

        values = [body_json["time"]]
        values += list(body_json["fields"].values())
        self.csv_writer.writerow(values)
        self.current_file.flush()
        self.number_records += 1
        self._l.debug(f"self.number_records={self.number_records}")

    def start_recording(self, rabbit_config):
        rabbitmq = Rabbitmq(**rabbit_config)
        rabbitmq.connect_to_server()

        try:
            rabbitmq.subscribe(routing_key=ROUTING_KEY_STATE,
                               on_message_callback=self.read_state)

            rabbitmq.start_consuming()
        except KeyboardInterrupt:
            rabbitmq.close()
