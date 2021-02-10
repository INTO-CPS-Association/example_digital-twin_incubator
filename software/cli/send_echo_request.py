import logging

from digital_twin.communication.rabbitmq_protocol import ROUTING_KEY_PTSIMULATOR4
from incubator.communication.server.rpc_client import RPCClient
from startup.utils.logging_config import config_logging

if __name__ == '__main__':
    config_logging("logs/echo_request.log", level=logging.WARN)
    client = RPCClient(ip="localhost")
    client.connect_to_server()
    reply = client.invoke_method(ROUTING_KEY_PTSIMULATOR4, "echo", {"msg": "Hello World!"})
    print(reply)
