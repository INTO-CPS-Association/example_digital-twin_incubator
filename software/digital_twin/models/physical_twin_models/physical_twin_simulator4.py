import logging

from communication.server.rpc_server import RPCServer
from communication.shared.connection_parameters import *
from communication.shared.protocol import ROUTING_KEY_PTSIMULATOR4


class PhysicalTwinSimulator4Params(RPCServer):

    def __init__(self, ip=RASPBERRY_IP,
                 port=RASPBERRY_PORT,
                 username=PIKA_USERNAME,
                 password=PIKA_PASSWORD,
                 vhost=PIKA_VHOST,
                 exchange_name=PIKA_EXCHANGE,
                 exchange_type=PIKA_EXCHANGE_TYPE
                 ):
        super().__init__(ip=ip,
                         port=port,
                         username=username,
                         password=password,
                         vhost=vhost,
                         exchange_name=exchange_name,
                         exchange_type=exchange_type)
        self._l = logging.getLogger("PhysicalTwinSimulator4Params")
    
    def start_serving(self):
        super(PhysicalTwinSimulator4Params, self).start_serving(ROUTING_KEY_PTSIMULATOR4, ROUTING_KEY_PTSIMULATOR4)
    
    def on_run_historical(self, args):
        start_date = args["start_date"]
