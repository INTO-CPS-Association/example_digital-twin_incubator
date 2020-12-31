"""
Contains the implementation of the component that is responsible for storing the data from the incubator in the influxdb database
"""
import logging

from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS

from communication.server.rabbitmq import Rabbitmq
from communication.shared.protocol import ROUTING_KEY_RECORDER
from digital_twin.data_access.dbmanager.data_access_parameters import INFLUXDB_TOKEN, INFLUXDB_ORG, INFLUXDB_BUCKET, \
    INFLUXDB_URL


class IncubatorDataRecorderInflux():
    def __init__(self):
        self._l = logging.getLogger("IncubatorDataRecorderInflux")
        self.write_api = None
        self.influx_db_org = None
        self.influxdb_bucket = None

    def read_record_request(self, ch, method, properties, body_json):
        self._l.debug("New record msg:")
        self._l.debug(body_json)
        self.write_api.write(self.influxdb_bucket, self.influx_db_org, body_json)

    def start_recording(self, rabbitmq_ip="localhost",
                        influx_url=INFLUXDB_URL,
                        influx_token=INFLUXDB_TOKEN,
                        influxdb_org=INFLUXDB_ORG,
                        influxdb_bucket=INFLUXDB_BUCKET
                        ):
        rabbitmq = Rabbitmq(ip=rabbitmq_ip)
        rabbitmq.connect_to_server()

        client = InfluxDBClient(url=influx_url, token=influx_token, org=influxdb_org)
        write_api = client.write_api(write_options=SYNCHRONOUS)
        self.write_api = write_api
        self.influx_db_org = influxdb_org
        self.influxdb_bucket = influxdb_bucket

        try:
            rabbitmq.subscribe(routing_key=ROUTING_KEY_RECORDER,
                               on_message_callback=self.read_record_request)

            rabbitmq.start_consuming()
        except KeyboardInterrupt:
            rabbitmq.close()
