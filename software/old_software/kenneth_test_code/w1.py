#!/usr/bin/python
# -*- coding: utf-8 -*-

import re,os, time

# function: read and parse sensor data file
def read_sensor(path):
  value = "U"
  try:
    f = open(path, "r")
    line = f.readline()
    if re.match(r"([0-9a-f]{2} ){9}: crc=[0-9a-f]{2} YES", line):
      line = f.readline()
      m = re.match(r"([0-9a-f]{2} ){9}t=([+-]?[0-9]+)", line)
      if m:
        value = str(float(m.group(2)) / 1000.0)
    f.close()
  except (IOError) as e:
    print(time.strftime("%x %X"), "Error reading", path, ": ", e)
  return value

# define pathes to 1-wire sensor data
pathes = (
  "/sys/bus/w1/devices/10-0008039a977a/w1_slave",
  "/sys/bus/w1/devices/10-0008039ad4ee/w1_slave",
  "/sys/bus/w1/devices/10-0008039b25c1/w1_slave"
)

# read sensor data
data = 'N'
for path in pathes:
  data += ':'
  print("Sensor %s = %s" % (path,str(read_sensor(path))))
  time.sleep(0.1)

