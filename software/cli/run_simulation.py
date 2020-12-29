import logging

from communication.server.rpc_client import RPCClient
from communication.shared.protocol import ROUTING_KEY_PTSIMULATOR4, from_s_to_ns
from startup.logging_config import config_logging

if __name__ == '__main__':
    config_logging(level=logging.WARN)
    client = RPCClient(ip="localhost")
    client.connect_to_server()
    reply = client.invoke_method(ROUTING_KEY_PTSIMULATOR4, "run_historical", {"start_date": from_s_to_ns(0.0),
                                                                              "end_date": from_s_to_ns(10.0),
                                                                              "record": False})
    print(reply)
