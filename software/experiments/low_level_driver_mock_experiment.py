import logging
import threading
import time

import pika
from experiments.config.config import config_logger
from pyhocon import ConfigFactory
from software.src.shared.protocol.protocol import ROUTING_KEY_HEATER

from external.dtwp.src.Experiments import ExperimentWithServices
from mock_plant.mock_connection import MOCK_HEATER_ON
from services.low_level_driver_mock import low_level_driver_mock
from services.rabbitmq_service import rabbitmq_service
from pathlib import Path
import os
from incubator.software.src.shared.communication.rabbitmq import Rabbitmq
import incubator.software.src.shared.communication.rabbitmq

class LowLevelDriverMockExperiment(ExperimentWithServices):
    # Rabbitmq_service has to write to a object passed with.
    rabbitmq_service = rabbitmq_service()
    logging_conf: Path = Path(os.path.dirname(__file__)).parent / "logging.conf"
    lldm = low_level_driver_mock(rabbitmq_service, logging_conf)
    consumeConnection = None

    if Path(logging_conf).exists():
        config_logger(logging_conf)
    _l = logging.getLogger("LowLevelDriverMockExperiment")

    def get_services(self):
        return [self.rabbitmq_service, self.lldm]

    def read_mock_heater_on(self, ch, method, properties, body_json):
        self._l.info("New msg:")
        self._l.info(body_json)


    def do_experiment(self):
        rmq_config = ConfigFactory.parse_string(self.rabbitmq_service.get_rabbitmq_conf())

        def startConsuming():
            try:
                with Rabbitmq(**rmq_config['rabbitmq']) as con:
                    self.consumeConnection = con
                    con.subscribe(MOCK_HEATER_ON, on_message_callback=self.read_mock_heater_on)
                    con.start_consuming()
            except pika.exceptions.StreamLostError:
                pass
            except pika.exceptions.ChannelWrongStateError:
                pass



        t = threading.Thread(target=startConsuming, daemon=True)
        with Rabbitmq(**rmq_config['rabbitmq']) as con:
            # Consume thread
            t.start()
            heater_on = True
            for i in range(3):
                con.send_message(ROUTING_KEY_HEATER, {"heater": heater_on})
                heater_on = not heater_on
                time.sleep(2)


    def describe(self):
        return '''Experiment starts the rabbitmq_service and makes it available to the low_level_driver_mock.
        The experiment sends a message to the low level driver to turning the heater on/off. and reads the related output.
        The experiments receives a message from the heater mock when the heater is turned on / off by the low level driver.
        The message from the heater mock is printed to the console. 
        
        The connection details are as follows:
        Low level driver: 
            Read heater command from controller via: ROUTING_KEY_HEATER
                Set directly on Heater Mock via object
            Read fan command from controller via: ROUTING_KEY_FAN
                Set directly on Fan Mock via object
            Send T1, T2, T3, Heater, Fan via: ROUTING_KEY_STATE
                T1, T2, T3 are acquired directly via Temperature Sensor Mocks
                Heater and Fan are acquired directly via HeaterMock and LEDMock respectively
        Temperature Sensor Mocks:
            Read Temperatur Via: MOCK_TEMP_T1, MOCK_TEMP_T2, MOCK_TEMP_T3 respectively
        Heater Mock
            Send On/Off via: MOCK_HEATER_ON
        Fan Mock (Actually just an LED mock):
            Does not send anything. 
            
        Thus the system inputs:
            ROUTING_KEY_HEATER
            ROUTING_KEY_FAN
            MOCK_TEMP_T1
            MOCK_TEMP_T2
            MOCK_TEMP_T3
        The system outputs:
            MOCK_HEATER_ON
            ROUTING_KEY_STATE         
        '''


if __name__ == '__main__':
    LowLevelDriverMockExperiment().run()
