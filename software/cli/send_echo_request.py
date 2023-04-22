import logging

from digital_twin.communication.rabbitmq_protocol import ROUTING_KEY_PTSIMULATOR4
from incubator.communication.server.rpc_client import RPCClient
from incubator.config.config import load_config
from startup.utils.logging_config import config_logging

if __name__ == '__main__':
    config_logging("logs/echo_request.log", level=logging.WARN)
    config = load_config("startup.conf")
    client = RPCClient(**(config["rabbitmq"]))
    client.connect_to_server()
    reply = client.invoke_method(ROUTING_KEY_PTSIMULATOR4, "echo", {"msg": "Hello World!"})
    print(reply)
