from time import sleep
import pika
import sys
import json

import wire1temperature as wire1
from gpiozero import LED

#id=12=heater, id=13=fan, and 1,2,3 for temperature sensors
heater = 12
fan =13

temperatureSensers = (
  "/sys/bus/w1/devices/10-0008039ad4ee/w1_slave",
 "/sys/bus/w1/devices/10-0008039b25c1/w1_slave",
  "/sys/bus/w1/devices/10-0008039a977a/w1_slave"
)

tempState = {"time":False,
             "sensorReading1":False,
             "sensorReading2":False,
             "sensorReading3":False
             }
def read_temperatures(ch, method, properties, body):
    for idx,key in enumerate(body):
        if idx >=1:
            if body[key]  == True:
                temp = wire1.read_sensor(temperatureSensers[idx-1])
                tempState["sensorReading" + str(idx)]=temp
            else:
                tempState["sensorReading" + str(idx)] = False
        else:
            if body[key]  == True:
                tempState["Time"]= "2019-01-04T16:41:24+02:00"
            else:
                tempState["Time"] = False
    print(tempState)
    channel.basic_publish(
        exchange='Incubator_AMQP', routing_key="incubator.hardware.w1.tempState", body=json.dumps(tempState))


    #topic  ="incubator/hardware/w1/"+str(idx)
    #print("Publishing %s %s"%(topic,temp))
    #client.publish(topic, temp);

#####################################rabbitmq connection
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='10.192.17.148'))
channel = connection.channel()

channel.exchange_declare(exchange='Incubator_AMQP', exchange_type='topic')

result = channel.queue_declare('', exclusive=True)
queue_name = result.method.queue

channel.queue_bind(
        exchange='Incubator_AMQP', queue=queue_name, routing_key="incubator.hardware.w1.tempReading")

channel.basic_consume(
    queue=queue_name, on_message_callback=read_temperatures, auto_ack=True)
