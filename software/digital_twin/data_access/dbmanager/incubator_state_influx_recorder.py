"""
Contains the implementation of the component that is responsible for storing the data from the incubator in the influxdb database
"""
import logging

from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS

from communication.server.rabbitmq import Rabbitmq
from communication.shared.protocol import decode_json, ROUTING_KEY_RECORDER


class IncubatorDataRecorderInflux():
    def __init__(self):
        self._l = logging.getLogger("IncubatorDataRecorderInflux")
        self.write_api = None
        self.influx_db_org = None
        self.influxdb_bucket = None

    def read_record_request(self, ch, method, properties, body):
        self._l.debug("New record msg:")
        data = decode_json(body)
        self._l.debug(data)
        self.write_api.write(self.influxdb_bucket, self.influx_db_org, data)

    def start_recording(self, rabbitmq_ip="localhost",
                        influx_url="http://localhost:8086",
                        influx_token="-g7q1xIvZqY8BA82zC7uMmJS1zeTj61SQjDCY40DkY6IpPBpvna2YoQPdSeENiekgVLMd91xA95smSkhhbtO7Q==",
                        influxdb_org="incubator",
                        influxdb_bucket="incubator"
                        ):
        rabbitmq = Rabbitmq(ip=rabbitmq_ip)
        rabbitmq.connect_to_server()

        client = InfluxDBClient(url=influx_url, token=influx_token)
        write_api = client.write_api(write_options=SYNCHRONOUS)
        self.write_api = write_api
        self.influx_db_org = influxdb_org
        self.influxdb_bucket = influxdb_bucket

        try:
            rabbitmq.subscribe(queue_name="record", routing_key=ROUTING_KEY_RECORDER,
                               on_message_callback=self.read_record_request)

            rabbitmq.start_consuming()
        except KeyboardInterrupt:
            rabbitmq.close()
