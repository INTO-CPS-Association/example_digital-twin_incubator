import logging
from datetime import datetime
from random import random
from time import sleep

from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    # You can generate a Token from the "Tokens Tab" in the UI
    token = "-g7q1xIvZqY8BA82zC7uMmJS1zeTj61SQjDCY40DkY6IpPBpvna2YoQPdSeENiekgVLMd91xA95smSkhhbtO7Q=="
    org = "incubator"
    bucket = "incubator"

    client = InfluxDBClient(url="http://localhost:8086", token=token)

    # Get write-api
    write_api = client.write_api(write_options=SYNCHRONOUS)

    while True:
        # Create a datapoint
        point = Point("test-data")\
            .tag("source", "test-script")\
            .field("test-field", random())\
            .time(datetime.utcnow(), WritePrecision.NS)

        # Send the point to DB
        write_api.write(bucket, org, point)

        print(point)

        sleep(1)




