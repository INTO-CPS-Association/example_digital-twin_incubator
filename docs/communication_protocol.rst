Communication Protocol
======================
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
            "readTemperature1": true or false
            "readTemperature2": true or false
            "readTemperature3": true or false
       }
    routing key: incubator.hardware.w1.tempReading

Temperature Reading
    | Message containing a temperature reading:
    .. code-block:: json

       {
            "time": timestamp
            "sensorReading1": value or false
            "sensorReading2": value or false
            "sensorReading3": value or false
       }
    routing key: incubator.hardware.w1.tempState

Issue a start/stop of the Fan
    | Message that starts/stops the fan:
    .. code-block:: json

       {
            "time": timestamp
            "startFan": true or false
       }
    routing key: incubator.hardware.gpio.fanManipulate

Issue a start/stop of the Heater
    | Message that starts/stops the heater:
    .. code-block:: json

       {
            "time": timestamp
            "startHeater": true or false
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
    
    
