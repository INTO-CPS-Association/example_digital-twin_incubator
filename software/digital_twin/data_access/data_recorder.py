"""
Contains the implementation of the component that is responsible for storing.
"""
import csv
import logging
import os
from datetime import datetime

from communication.server.rabbitmq import Rabbitmq, ROUTING_KEY_STATE
from communication.shared.protocol import decode_json


class IncubatorDataRecorder():
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

    def read_state(self, ch, method, properties, body):
        self._l.debug("New msg:")
        body_json = decode_json(body)
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
            header = list(body_json.keys())
            self.csv_writer.writerow(header)
            self.header_written = True

        values = list(body_json.values())
        self.csv_writer.writerow(values)
        self.current_file.flush()
        self.number_records += 1
        self._l.debug(f"self.number_records={self.number_records}")

    def start_recording(self, rabbitmq_ip):
        rabbitmq = Rabbitmq(ip=rabbitmq_ip)
        state_queue_name = 'state'
        rabbitmq.connect_to_server()

        try:
            rabbitmq.declare_queue(queue_name=state_queue_name, routing_key=ROUTING_KEY_STATE)
            rabbitmq.channel.basic_consume(queue=state_queue_name,
                                           on_message_callback=self.read_state,
                                           auto_ack=True)
            rabbitmq.channel.start_consuming()
        except KeyboardInterrupt:
            rabbitmq.close()
