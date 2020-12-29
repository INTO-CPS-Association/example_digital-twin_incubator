import logging
from datetime import datetime

from communication.server.rpc_client import RPCClient
from communication.shared.protocol import ROUTING_KEY_PTSIMULATOR4, from_s_to_ns
from startup.logging_config import config_logging

DATE_FORMAT = "%Y-%m-%dT%H:%M:%S.%f"

if __name__ == '__main__':
    def get_date_ns(date_string):
        return from_s_to_ns(datetime.strptime(date_string, DATE_FORMAT).timestamp())

    start_date = get_date_ns('2020-12-29T09:40:00.00')
    end_date = get_date_ns('2020-12-29T09:50:00.00')

    config_logging(level=logging.WARN)
    client = RPCClient(ip="localhost")
    client.connect_to_server()
    reply = client.invoke_method(ROUTING_KEY_PTSIMULATOR4, "run_historical", {"start_date": start_date,
                                                                              "end_date": end_date,
                                                                              "record": False})
    print(reply)
