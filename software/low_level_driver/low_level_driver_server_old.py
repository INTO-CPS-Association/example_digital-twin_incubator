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
heater = 12
fan =13
led_fan = LED(fan)
led_heater = LED(heater)



temperatureSensers = (
  "/sys/bus/w1/devices/10-0008039ad4ee/w1_slave",
 "/sys/bus/w1/devices/10-0008039b25c1/w1_slave",
  "/sys/bus/w1/devices/10-0008039a977a/w1_slave"
)

tempState = {"Time":False,
             "sensorReading1":False,
             "sensorReading2":False,
             "sensorReading3":False
             }
def read_temperatures(ch, method, properties, body):
    print(" [x] %r:%r" % (method.routing_key, body))
    #print(type(body))
    body = json.loads(body)
    #print(type(body))
    for idx,key in enumerate(body):
        #print("idx is",idx,"key is",key)
        if idx >=1:
            if body[key]  == True:
                temp = wire1.read_sensor(temperatureSensers[idx-1])
                tempState["sensorReading" + str(idx)]=temp
            else:
                tempState["sensorReading" + str(idx)] = False
        else:
            if body[key]  == True:
                # seconds = time.time()
               # local_time = time.ctime(seconds)
                tempState["Time"]= datetime.datetime.now().replace(microsecond=0,tzinfo=datetime.timezone.utc).isoformat()
            else:
                tempState["Time"] = False
    print(tempState)
    channel.basic_publish(
        exchange='Incubator_AMQP', routing_key="incubator.hardware.w1.tempState", body=json.dumps(tempState))
    print("Keep listening")

def ctrlFan(ch, method, properties, body):
    print(" [x] %r:%r" % (method.routing_key, body))
    #print(type(body))
    body = json.loads(body)
    for idx,key in enumerate(body):
        #print("idx is",idx,"key is",key)
        if idx >=1:
            if body[key]  == True:
                led_fan.on()
            if body[key]  == False:
                led_fan.off()
        else:
            if body[key]  == True:
                # seconds = time.time()
                # local_time = time.ctime(seconds)
                tempState["Time"]= datetime.datetime.now().replace(microsecond=0,tzinfo=datetime.timezone.utc).isoformat()
            else:
                tempState["Time"] = False
    # channel.basic_publish(
    #     exchange='Incubator_AMQP', routing_key="incubator.hardware.w1.tempState", body=json.dumps(tempState))
    print("Keep listening")

def ctrlheater(ch, method, properties, body):
    print(" [x] %r:%r" % (method.routing_key, body))
    # print(type(body))
    body = json.loads(body)
    for idx, key in enumerate(body):
        # print("idx is",idx,"key is",key)
        if idx >= 1:
            if body[key] == True:
                led_heater.on()
            if body[key] == False:
                led_heater.off()
        else:
            if body[key] == True:
                # seconds = time.time()
                # local_time = time.ctime(seconds)
                tempState["Time"] = datetime.datetime.now().replace(microsecond=0,tzinfo=datetime.timezone.utc).isoformat()
            else:
                tempState["Time"] = False
        # channel.basic_publish(
        #     exchange='Incubator_AMQP', routing_key="incubator.hardware.w1.tempState", body=json.dumps(tempState))
    print("Keep listening")


    #topic  ="incubator/hardware/w1/"+str(idx)
    #print("Publishing %s %s"%(topic,temp))
    #client.publish(topic, temp);

#####################################rabbitmq connection
IP_raspberry = '10.17.98.141'
IP_myLaptop =  '10.17.98.164'
credentials = pika.PlainCredentials('incubator', 'incubator')
parameters = pika.ConnectionParameters(IP_raspberry,
                                   5672,
                                   '/',
                                   credentials)
connection = pika.BlockingConnection(parameters)
#connection = pika.BlockingConnection(
#    pika.ConnectionParameters(host='10.192.17.148',port=1883))
channel = connection.channel()

channel.exchange_declare(exchange='Incubator_AMQP', exchange_type='topic')
################################
result = channel.queue_declare('', exclusive=True)
queue_name = result.method.queue
channel.queue_bind(
        exchange='Incubator_AMQP', queue=queue_name, routing_key="incubator.hardware.w1.tempReading")
channel.basic_consume(
    queue=queue_name, on_message_callback=read_temperatures, auto_ack=True)

# resultsss = channel.queue_declare('', exclusive=True)
# queue_names = resultsss.method.queue
# channel.queue_bind(
#         exchange='Incubator_AMQP', queue=queue_names, routing_key="incubator.hardware.gpio.fanManipulate")
# channel.basic_consume(
#     queue=queue_names, on_message_callback=ctrlFan, auto_ack=True)
#
# resultss = channel.queue_declare('', exclusive=True)
# queue_namess = resultss.method.queue
# channel.queue_bind(
#         exchange='Incubator_AMQP', queue=queue_namess, routing_key="incubator.hardware.gpio.heaterManipulate")
# channel.basic_consume(
#     queue=queue_namess, on_message_callback=ctrlheater, auto_ack=True)

result = channel.queue_declare('2', exclusive=True)
queue_name = result.method.queue
channel.queue_bind(
        exchange='Incubator_AMQP', queue=queue_name, routing_key="incubator.hardware.gpio.fanManipulate")
channel.basic_consume(
    queue=queue_name, on_message_callback=ctrlFan, auto_ack=True)


print("listening")
channel.start_consuming()
