import logging
from datetime import datetime
from random import random
from time import sleep

from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

from config.config import config_logger, load_config

if __name__ == '__main__':

    config_logger("logging.conf")
    config = load_config("startup.conf")

    client = InfluxDBClient(**config["influxdb"])

    # Get write-api
    write_api = client.write_api(write_options=SYNCHRONOUS)

    n = 1

    while n>0:
        # Create a datapoint
        point = Point("test-data")\
            .tag("source", "test-script")\
            .field("test-field", random())\
            .time(datetime.utcnow(), WritePrecision.NS)

        # Send the point to DB
        write_api.write(bucket, org, point)

        print(point)

        sleep(1)
        n -= 1

    query_api = client.query_api()
    results = query_api.query_data_frame(f"""
    from(bucket: "{bucket}")
      |> range(start: -10h, stop: now())
      |> filter(fn: (r) => r["_measurement"] == "test-data")
      |> filter(fn: (r) => r["_field"] == "test-field")
    """)

    print(results[["_time","_value"]])




