Communication Protocol
======================

There are two protocols to consider here:

A. Communication with low_level_driver

B. Communication with rabbitmq fmu.

Communication with low_level_driver
-----------------------------------

Specified in the python class ``IncubatorDriver``.
Essentially, a single message is published for each control loop execution.
That message contains the readings of all temperature sensors, and state of the controller (parameters, etc.).


Communication with RabbitMQ FMU
-------------------------------

The protocol has to match with https://into-cps-rabbitmq-fmu.readthedocs.io/en/latest/user-manual.html


RabbitMQ Topics
---------------
| Messages going to IO: incubator.toio
| Messages going to controller: incubator.tocontroller

RabbitMQ Messages
-----------------

Issue a temperature reading
    | Message that initiates a temperature reading:

    .. code-block:: json

       {
            "time": timestamp
            "readTemperature1": True or False
            "readTemperature2": True or False
            "readTemperature3": True or False
       }

    routing key: incubator.hardware.w1.tempRead


Temperature Reading
    | Message containing a temperature reading:

    .. code-block:: json

       {
            "time": timestamp
            "sensorReading1": value or False
            "sensorReading2": value or False
            "sensorReading3": value or False
       }

    routing key: incubator.hardware.w1.tempState

Issue a start/stop of the Fan
    | Message that starts/stops the fan:

    .. code-block:: json

       {
            "time": timestamp
            "startFan": True or False
       }

    routing key: incubator.hardware.gpio.fanManipulate

Issue a start/stop of the Heater
    | Message that starts/stops the heater:

    .. code-block:: json

       {
            "time": timestamp
            "startHeater": True or False
       }

    routing key: incubator.hardware.gpio.heaterManipulate

Change the value of a parameter
    | Message that changes the value of a parameter

    .. code-block:: json

       {
            "time": timestamp
            "Upper temperature": Value or False
            "Lower temperature": Value or False
            "Dissipation delay": Value or False
            "Heater on for X": Value or False
       }

    routing key: incubator.hardware.gpio.paraChange
    
    
