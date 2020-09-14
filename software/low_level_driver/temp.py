from time import sleep
import pika
import sys
import json
import ast
import time
import datetime
import wire1temperature as wire1
from gpiozero import LED

#id=12=heater, id=13=fan, and 1,2,3 for temperature sensors
# def connectionParas()

class IncubatorControl:
    def __init__(self,IP_raspberry='10.17.98.141',
                 port=5672,
                 username='incubator',
                 password='incubator',
                 vhost='/',
                 exchangename='Incubator_AMQP',
                 exchange_type='topic',
                 ):
        self.IP_raspberry = IP_raspberry
        self.port = port
        self.username=username
        self.password = password
        self.vhost = vhost
        self.exchangename = exchangename
        self.exchange_type = exchange_type
        self.temperatureSensers = ("/sys/bus/w1/devices/10-0008039ad4ee/w1_slave",
                                   "/sys/bus/w1/devices/10-0008039b25c1/w1_slave",
                                   "/sys/bus/w1/devices/10-0008039a977a/w1_slave"
                                   )
        self.tempState = {"Time":False,
                          "sensorReading1":False,
                          "sensorReading2":False,
                          "sensorReading3":False
                          }
        self.heater = 12
        self.fan = 13
        self.led_fan = LED(self.fan)
        self.led_heater = LED(self.heater)
        # self.numberofqueues = numberofqueues

    def connectionToserver(self):
        self.credentials = pika.PlainCredentials(self.username, self.password)
        self.parameters = pika.ConnectionParameters(self.IP_raspberry,
                                                    5672,
                                                    '/',
                                                    self.credentials)
        self.connection = pika.BlockingConnection(self.parameters)
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange=self.exchangename, exchange_type=self.exchange_type)

    def queueDeclare(self, callbackFunc, queuename="1", routingkey="incubator.hardware.w1.tempReading"):
        self.result = self.channel.queue_declare(queuename, exclusive=True)
        self.queue_name = self.result.method.queue
        self.channel.queue_bind(
            exchange=self.exchangename,
            queue=self.queue_name,
            routing_key=routingkey
        )
        self.channel.basic_consume(
            queue=self.queue_name,
            on_message_callback=callbackFunc,
            auto_ack=True
        )

    def startListening(self):
        print("Startinh listening")
        self.channel.start_consuming()

    def read_temperatures(self,ch, method, properties, body):
        print(" [x] %r:%r" % (method.routing_key, body))
        # print(type(body))
        self.body = json.loads(body)
        # print(type(body))
        for self.idx, self.key in enumerate(self.body):
            # print("idx is",idx,"key is",key)
            if self.idx >= 1:
                if self.body[self.key] == True:
                    self.temp = wire1.read_sensor(self.temperatureSensers[self.idx - 1])
                    self.tempState["sensorReading" + str(self.idx)] = self.temp
                else:
                    self.tempState["sensorReading" + str(self.idx)] = False
            else:
                if self.body[self.key] == True:
                    # seconds = time.time()
                    # local_time = time.ctime(seconds)
                    self.tempState["Time"] = datetime.datetime.now().replace(microsecond=0,
                                                                        tzinfo=datetime.timezone.utc).isoformat()
                else:
                    self.tempState["Time"] = False
        print(self.tempState)
        self.channel.basic_publish(
            exchange=self.exchangename, routing_key="incubator.hardware.w1.tempState", body=json.dumps(self.tempState))
        print("Keep listening")

if __name__ == '__main__':
    incubator = IncubatorControl()
    incubator.connectionToserver()
    incubator.queueDeclare(incubator.read_temperatures)
    incubator.startListening()

