import time

import pika
import json
import datetime
from gpiozero import LED
import temperature_sensor_read


class IncubatorDriver:
    def __init__(self, ip_raspberry='10.17.98.141',
                 port=5672,
                 username='incubator',
                 password='incubator',
                 vhost='/',
                 exchange_name='Incubator_AMQP',
                 exchange_type='topic',
                 heater_pin=12,
                 fan_pin=13,
                 simulate_actuation=True
                 ):

        # Connection info
        self.vhost = vhost
        self.exchange_name = exchange_name
        self.exchange_type = exchange_type

        credentials = pika.PlainCredentials(username, password)
        self.parameters = pika.ConnectionParameters(ip_raspberry,
                                                    port,
                                                    '/',
                                                    credentials)
        self.connection = None

        # TODO: What is this doing here?
        self.tempState = {"Time": False,
                          "sensorReading1": False,
                          "sensorReading2": False,
                          "sensorReading3": False
                          }

        # IO
        self.heater = LED(heater_pin)
        self.fan = LED(fan_pin)
        self.temperature_sensor = ("/sys/bus/w1/devices/10-0008039ad4ee/w1_slave",
                                   "/sys/bus/w1/devices/10-0008039b25c1/w1_slave",
                                   "/sys/bus/w1/devices/10-0008039a977a/w1_slave"
                                   )

        # Safety
        self.simulate_actuation = simulate_actuation

        # Always start in safe mode.
        self.fan.off()
        self.heater.off()

    def connect_to_server(self):
        self.connection = pika.BlockingConnection(self.parameters)
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange=self.exchange_name, exchange_type=self.exchange_type)

        self.declare_queue(self.on_temperature_read_msg, queue_name="0",
                           routing_key="incubator.hardware.w1.tempRead")
        self.declare_queue(self.on_fan_control_msg, queue_name="1", routing_key="incubator.hardware.gpio.fanManipulate")
        self.declare_queue(self.on_heat_control_message, queue_name="heater_control",
                           routing_key="incubator.hardware.gpio.heaterManipulate")

    def declare_queue(self, callback, queue_name, routing_key):
        self.channel.queue_declare(queue_name, exclusive=True)
        self.channel.queue_bind(
            exchange=self.exchange_name,
            queue=queue_name,
            routing_key=routing_key
        )
        # self.channel.basic_consume(
        #     queue=queue_name,
        #     on_message_callback=callback,
        #     auto_ack=True
        # )
        # print("Bind ", routing_key, " with queue name ", queue_name)

    def start_listening(self):
        print("Start listening")
        self.channel.start_consuming()

    def on_temperature_read_msg(self, ch, method, properties, body):
        print("Received Routing Key:%r \n Messages:%r" % (method.routing_key, body))
        # print(type(body))
        body = json.loads(body)
        # print(type(body))
        for idx, key in enumerate(body):
            # print("idx is",idx,"key is",key)
            if idx >= 1:
                if body[key] == True:
                    temp = temperature_sensor_read.read_sensor(self.temperature_sensor[idx - 1])
                    self.tempState["sensorReading" + str(self.idx)] = temp
                else:
                    self.tempState["sensorReading" + str(self.idx)] = False
            else:
                if body[key] == True:
                    # seconds = time.time()
                    # local_time = time.ctime(seconds)
                    self.tempState["Time"] = datetime.datetime.now().replace(microsecond=0,
                                                                             tzinfo=datetime.timezone.utc).isoformat()
                else:
                    self.tempState["Time"] = False
        self.channel.basic_publish(
            exchange=self.exchange_name, routing_key="incubator.hardware.w1.tempState", body=json.dumps(self.tempState))
        print("Published Messages: ", self.tempState)
        print("Keep listening")

    def on_fan_control_msg(self, ch, method, properties, body):
        print("Received Routing Key:%r \n Messages:%r" % (method.routing_key, body))
        # print(type(body))
        self.body = json.loads(body)
        for self.idx, self.key in enumerate(self.body):
            # print("idx is",idx,"key is",key)
            if self.idx >= 1:
                if self.body[self.key] == True:
                    if not self.simulate_actuation:
                        self.fan.on()
                    else:
                        print("Pretending to turn the fan on.")
                if self.body[self.key] == False:
                    if not self.simulate_actuation:
                        self.fan.off()
                    else:
                        print("Pretending to turn the fan off.")
            else:
                if self.body[self.key] == True:
                    # seconds = time.time()
                    # local_time = time.ctime(seconds)
                    self.tempState["Time"] = datetime.datetime.now().replace(microsecond=0,
                                                                             tzinfo=datetime.timezone.utc).isoformat()
                else:
                    self.tempState["Time"] = False
        # channel.basic_publish(
        #     exchange='Incubator_AMQP', routing_key="incubator.hardware.w1.tempState", body=json.dumps(tempState))
        print("Keep listening")

    def on_heat_control_message(self, ch, method, properties, body):
        print("Received Routing Key:%r \n Messages:%r" % (method.routing_key, body))
        # print(type(body))
        self.body = json.loads(body)
        for self.idx, self.key in enumerate(self.body):
            # print("idx is",idx,"key is",key)
            if self.idx >= 1:
                if self.body[self.key] == True:
                    if not self.simulate_actuation:
                        self.heater.on()
                    else:
                        print("Pretending to turn the heater on.")
                if self.body[self.key] == False:
                    if not self.simulate_actuation:
                        self.heater.off()
                    else:
                        print("Pretending to turn the heater off.")
            else:
                if self.body[self.key] == True:
                    self.tempState["Time"] = datetime.datetime.now().replace(microsecond=0,
                                                                             tzinfo=datetime.timezone.utc).isoformat()
                else:
                    self.tempState["Time"] = False
        print("Keep listening")


if __name__ == '__main__':
    incubator = IncubatorDriver()
    incubator.connect_to_server()

    time.sleep(5)

    (method, properties, body) = incubator.channel.basic_get("heater_control", auto_ack=True)
    print(f"Ctrl message received: {(method, properties, body)}")

    #incubator.start_listening()
    print("Started Listening.")
