#!/usr/bin/env python3
import paho.mqtt.client as mqtt
import time

import wire1temperature as wire1
from gpiozero import LED

heaterGpio=12
fanGpio=13


# /incubator/hardware/w1/1

temperatureSensers = (
  "/sys/bus/w1/devices/10-0008039ad4ee/w1_slave",
 "/sys/bus/w1/devices/10-0008039b25c1/w1_slave",
  "/sys/bus/w1/devices/10-0008039a977a/w1_slave"
)

def read_temperatures():
  for idx,path in enumerate(temperatureSensers):
    temp = wire1.read_sensor(path)
    topic  ="incubator/hardware/w1/"+str(idx)
    print("Publishing %s %s"%(topic,temp))
    client.publish(topic, temp);


#(wire1.read_sensor("/sys/bus/w1/devices/10-0008039a977a/w1_slave"))

# Create client instance and connect to localhost
client = mqtt.Client()
client.connect("10.17.98.106",1883,60)

print("Connected")

for i in range(0,100):
  read_temperatures()

time.sleep(2)



# example of io 
#led = LED(12)
#
#while True:
#    led.on()
#    sleep(30)
#    led.off()
#    sleep(30)



client.disconnect();
