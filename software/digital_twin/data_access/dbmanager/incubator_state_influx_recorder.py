"""
Contains the implementation of the component that is responsible for storing the data from the incubator in the influxdb database
"""
import logging

from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS

from digital_twin.communication.rabbitmq_protocol import ROUTING_KEY_RECORDER
from incubator.communication.server.rabbitmq import Rabbitmq


class IncubatorDataRecorderInflux:
    def __init__(self):
        self._l = logging.getLogger("IncubatorDataRecorderInflux")
        self.write_api = None
        self.influx_db_org = None
        self.influxdb_bucket = None
        self.rabbitmq = None

    def read_record_request(self, ch, method, properties, body_json):
        self._l.debug("New record msg:")
        self._l.debug(body_json)
        self.write_api.write(self.influxdb_bucket, self.influx_db_org, body_json)

    def setup(self, rabbitmq_config, influxdb_config):
        self.rabbitmq = Rabbitmq(**rabbitmq_config)
        self.rabbitmq.connect_to_server()

        client = InfluxDBClient(**influxdb_config)
        write_api = client.write_api(write_options=SYNCHRONOUS)
        self.write_api = write_api
        self.influx_db_org = influxdb_config["org"]
        self.influxdb_bucket = influxdb_config["bucket"]

        self.rabbitmq.subscribe(routing_key=ROUTING_KEY_RECORDER,
                           on_message_callback=self.read_record_request)

    def start_recording(self):
        try:
            self.rabbitmq.start_consuming()
        except KeyboardInterrupt:
            self.rabbitmq.close()
