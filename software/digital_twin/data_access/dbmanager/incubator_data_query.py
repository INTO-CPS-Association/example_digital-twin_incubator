import logging

import pandas
from influxdb_client import InfluxDBClient

from digital_twin.data_access.dbmanager.data_access_parameters import INFLUXDB_TOKEN, INFLUXDB_ORG, INFLUXDB_BUCKET


class IncubatorDataQuery:
    def __init__(self, url="http://localhost:8086",
                 token=INFLUXDB_TOKEN,
                 org=INFLUXDB_ORG,
                 bucket=INFLUXDB_BUCKET):
        self._client = None
        self._query = None
        self._influx_url = url
        self._influx_token = token
        self._influxdb_org = org
        self._influxdb_bucket = bucket
        self._l = logging.getLogger("IncubatorDataQuery")

    def connect(self):
        if self._client is None:
            self._client = InfluxDBClient(url=self._influx_url, token=self._influx_token, org=self._influxdb_org)
            self._l.debug(f"Initialized influxdb client for url {self._influx_url}.")

        if self._query is None:
            self._query = self._client.query_api()
            self._l.debug(f"Initialized query api.")

    def disconnect(self):
        if self._client is not None:
            self._l.debug(f"Disconnecting.")
            self._client.close()
            self._client = None
            self._query = None

    def query(self, start_date, end_date, measurement, field):
        self.connect()
        result = self._query.query_data_frame(f"""
            from(bucket: "{self._influxdb_bucket}")
              |> range(start: time(v: {start_date}), stop: time(v: {end_date}))
              |> filter(fn: (r) => r["_measurement"] == "{measurement}")
              |> filter(fn: (r) => r["_field"] == "{field}")
            """)
        assert isinstance(result, pandas.DataFrame), "Result is a dataframe"
        self._l.debug(f"New query for {measurement}'s {field}: {len(result)} samples retrieved.")
        return result

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, type, value, traceback):
        self.disconnect()
