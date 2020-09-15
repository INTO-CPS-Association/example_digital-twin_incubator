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
                 simulate_actuation=False
                 ):
        self.ip_raspberry = ip_raspberry
        self.port = port
        self.username = username
        self.password = password
        self.vhost = vhost
        self.exchange_name = exchange_name
        self.exchange_type = exchange_type
        self.simulate_actuation = simulate_actuation
        self.temperature_sensor = ("/sys/bus/w1/devices/10-0008039ad4ee/w1_slave",
                                   "/sys/bus/w1/devices/10-0008039b25c1/w1_slave",
                                   "/sys/bus/w1/devices/10-0008039a977a/w1_slave"
                                   )
        # TODO: What is this doing here?
        self.tempState = {"Time": False,
                          "sensorReading1": False,
                          "sensorReading2": False,
                          "sensorReading3": False
                          }
        self.heater = LED(heater_pin)
        self.fan = LED(fan_pin)

        # Always start in safe mode.
        self.fan.off()
        self.heater.off()

    def connect_to_server(self):
        self.credentials = pika.PlainCredentials(self.username, self.password)
        self.parameters = pika.ConnectionParameters(self.ip_raspberry,
                                                    5672,
                                                    '/',
                                                    self.credentials)
        self.connection = pika.BlockingConnection(self.parameters)
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange=self.exchange_name, exchange_type=self.exchange_type)

        self.declare_queue(self.on_temperature_read_msg, queuename="0",
                           routingkey="incubator.hardware.w1.tempRead")
        self.declare_queue(self.on_fan_control_msg, queuename="1", routingkey="incubator.hardware.gpio.fanManipulate")
        self.declare_queue(self.on_heat_control_message, queuename="2",
                           routingkey="incubator.hardware.gpio.heaterManipulate")

    def declare_queue(self, callbackFunc, queuename, routingkey):
        self.result = self.channel.queue_declare(queuename, exclusive=True)
        self.queue_name = self.result.method.queue
        self.channel.queue_bind(
            exchange=self.exchange_name,
            queue=self.queue_name,
            routing_key=routingkey
        )
        self.channel.basic_consume(
            queue=self.queue_name,
            on_message_callback=callbackFunc,
            auto_ack=True
        )
        print("Bind ", routingkey, " with queue name ", queuename)

    def start_listening(self):
        print("Start listening")
        self.channel.start_consuming()

    def on_temperature_read_msg(self, ch, method, properties, body):
        print(" Received Routing Key:%r \n Messages:%r" % (method.routing_key, body))
        # print(type(body))
        self.body = json.loads(body)
        # print(type(body))
        for self.idx, self.key in enumerate(self.body):
            # print("idx is",idx,"key is",key)
            if self.idx >= 1:
                if self.body[self.key] == True:
                    self.temp = temperature_sensor_read.read_sensor(self.temperature_sensor[self.idx - 1])
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
        self.channel.basic_publish(
            exchange=self.exchange_name, routing_key="incubator.hardware.w1.tempState", body=json.dumps(self.tempState))
        print("Published Messages: ", self.tempState)
        print("Keep listening")

    def on_fan_control_msg(self, ch, method, properties, body):
        print(" Received Routing Key:%r \n Messages:%r" % (method.routing_key, body))
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
        print(" Received Routing Key:%r \n Messages:%r" % (method.routing_key, body))
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
    incubator.start_listening()
    print("Started Listening.")
