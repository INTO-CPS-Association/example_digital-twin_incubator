import logging
from datetime import datetime, timedelta

from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS

from communication.shared.protocol import from_s_to_ns
from digital_twin.data_access.dbmanager.data_access_parameters import INFLUXDB_TOKEN, INFLUXDB_ORG, INFLUXDB_BUCKET, \
    INFLUXDB_URL
from digital_twin.models.plant_models.room_temperature_model import room_temperature
from startup.logging_config import config_logging
import numpy as np

if __name__ == '__main__':
    # Time range for the fake data
    end_date = datetime.now()
    start_date = end_date - timedelta(hours=10)

    start_date_s = start_date.timestamp()
    end_date_s = end_date.timestamp()

    config_logging(level=logging.WARN)

    token = INFLUXDB_TOKEN
    org = INFLUXDB_ORG
    bucket = INFLUXDB_BUCKET

    client = InfluxDBClient(url=INFLUXDB_URL, token=token, org=org)

    # Get write-api
    write_api = client.write_api(write_options=SYNCHRONOUS)

    # Construct points
    timerange_s = np.arange(start_date_s, end_date_s, 3.0)

    def point(t):
        t_ns = from_s_to_ns(t)
        return {
                    "measurement": "low_level_driver",
                    "time": t_ns,
                    "tags": {
                        "source": "low_level_driver"
                    },
                    "fields": {
                        "t1": room_temperature(t),
                        "time_t1": t_ns,
                    }
                }

    points = [point(t) for t in timerange_s]

    # Write them to DB
    write_api.write(bucket, org, points)
