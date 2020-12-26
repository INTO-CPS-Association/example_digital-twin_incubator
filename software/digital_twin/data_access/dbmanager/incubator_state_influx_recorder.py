"""
Contains the implementation of the component that is responsible for storing the data from the incubator in the influxdb database
"""
import csv
import logging
import os
from datetime import datetime

from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

from communication.server.rabbitmq import Rabbitmq, ROUTING_KEY_STATE
from communication.shared.protocol import decode_json


class IncubatorDataRecorderInflux():
    def __init__(self):
        self._l = logging.getLogger("IncubatorDataRecorderInflux")
        self.write_api = None
        self.influx_db_org = None
        self.influxdb_bucket = None

    def read_state(self, ch, method, properties, body):
        self._l.debug("New msg:")
        data = decode_json(body)
        self._l.debug(data)

        points = [
            {
                "measurement": "plant",
                "time": datetime.utcfromtimestamp(data["time"]),
                "tags": {
                    "source": "Recorder"
                },
                "fields": {
                    "t1": data["t1"],
                    "t2": data["t2"],
                    "t3": data["t3"],
                    "average_temperature": (data["t2"] + data["t3"])/2
                }
            },
            {
                "measurement": "controller",
                "time": datetime.utcfromtimestamp(data["time"]),
                "tags": {
                    "source": "Recorder"
                },
                "fields": {
                    "heater_on": data["heater_on"],
                    "fan_on": data["fan_on"],
                    "execution_interval": data["execution_interval"],
                    "elapsed": data["elapsed"]
                }
            }
        ]

        self.write_api.write(self.influxdb_bucket, self.influx_db_org, points)
        self._l.debug("Data sent to db: ")
        self._l.debug(points)

    def start_recording(self, rabbitmq_ip="localhost",
                        influx_url="http://localhost:8086",
                        influx_token="-g7q1xIvZqY8BA82zC7uMmJS1zeTj61SQjDCY40DkY6IpPBpvna2YoQPdSeENiekgVLMd91xA95smSkhhbtO7Q==",
                        influxdb_org="incubator",
                        influxdb_bucket="incubator"
                        ):
        rabbitmq = Rabbitmq(ip=rabbitmq_ip)
        state_queue_name = 'state'
        rabbitmq.connect_to_server()

        client = InfluxDBClient(url=influx_url, token=influx_token)
        write_api = client.write_api(write_options=SYNCHRONOUS)
        self.write_api = write_api
        self.influx_db_org = influxdb_org
        self.influxdb_bucket = influxdb_bucket

        try:
            rabbitmq.subscribe(queue_name=state_queue_name, routing_key=ROUTING_KEY_STATE,
                               on_message_callback=self.read_state)

            rabbitmq.start_consuming()
        except KeyboardInterrupt:
            rabbitmq.close()
