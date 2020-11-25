#!/usr/bin/env python
#from IOPi import IOPi
import time
import paho.mqtt.client as mqtt


def on_connect(client, userdata, flags, rc):
  print("Connected with result code "+str(rc))
  client.subscribe("incubator/#")

def on_message(client, userdata, msg):
  print("Message received-> " + msg.topic + " " + str(msg.payload)) 
#  print(userdata)
#  print(msg)
#  p,s = msg.payload.decode().split(",")
#  print(p)
#  print(s)
#  if (int(p) <= 16):
#    print("IO Bus 0 Pin: " + p)
#    print("IO Bus 0 mode: " + s)
#    iobus.write_pin(int(p), int(s))
#  else:
#    print("IO Bus 1 Pin: " + p)
#    print("IO Bus 1 mode: " + s)
#    iobusb.write_pin((int(p) -16), int(s))


client = mqtt.Client()
client.connect("localhost",1883,60)

client.on_connect = on_connect
client.on_message = on_message
client.loop_forever()
