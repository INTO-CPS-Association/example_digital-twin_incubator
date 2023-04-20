import logging
from datetime import datetime
from random import random
from time import sleep

from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

from incubator.config.config import config_logger, load_config

if __name__ == '__main__':

    config_logger("logging.conf")
    config = load_config("startup.conf")

    client = InfluxDBClient(**config["influxdb"])

    # Get write-api
    write_api = client.write_api(write_options=SYNCHRONOUS)

    N = 10

    bucket = config["influxdb"]["bucket"]
    org = config["influxdb"]["org"]

    print(f"Sending {N} data points to influxdb...")

    n = N
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

    print(f"Sent {N} data points to influxdb.")
    
    print(f"Reading {N} data points from influxdb...")
    
    query_string = f"""
    from(bucket: "{bucket}")
      |> range(start: -10h, stop: now())
      |> filter(fn: (r) => r["_measurement"] == "test-data")
      |> filter(fn: (r) => r["_field"] == "test-field")
      |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
    """

    print(f"Query used:")
    print(query_string)

    query_api = client.query_api()

    results = query_api.query_data_frame(query_string)

    print(results[["_time","test-field"]])

    print(f"Read {N} data points from influxdb.")