import logging

from communication.server.rpc_client import RPCClient
from communication.shared.protocol import ROUTING_KEY_PTSIMULATOR4
from startup.logging_config import config_logging

if __name__ == '__main__':
    config_logging("echo_request.log", level=logging.DEBUG)
    client = RPCClient(ip="localhost")
    client.connect_to_server()
    reply = client.invoke_method(ROUTING_KEY_PTSIMULATOR4, "echo", {"msg": "Hello World!"})
    print(reply)
