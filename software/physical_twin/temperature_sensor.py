#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import time


def read_sensor(path):
    """
    read and parse sensor data file
    :param path: 
    :return: 
    """
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
    except IOError as e:
        print(time.strftime("%x %X"), "Error reading", path, ": ", e)
        raise e
    return value
