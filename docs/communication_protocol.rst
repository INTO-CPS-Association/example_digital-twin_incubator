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
    routing key: incubator.hardware.gpio.tempReading

Temperature Reading
    | Message containing a temperature reading:
    | :code:`tempKXXXXX`  #K represents the order of the sensors and XXXXX means the real tempture*1000

Issue a start/stop of the Fan
    | Message that starts/stops the fan:
    | :code:`fan2on/fan2off` 

Issue a start/stop of the Heater
    | Message that starts/stops the heater:
    | :code:`heater2on/heater2off`

Change the value of a parameter
    | Message that changes the value of a parameter
    | :code:`parachKXXXXX` #K represents the order of the parameters defined in the file of claudio's. XXXXX means the replaced parameter value. iF it is temperture then the real temperture * 1000. 
