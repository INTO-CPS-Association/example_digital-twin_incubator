Communication Protocol
======================

RabbitMQ Messages
-----------------

Issue a temperature reading
    | Message that initiates a temperature reading:
    | :code:`tempreadK` #K represents the order of the sensors

Temperature Reading
    | Message containing a temperature reading:
    | :code:`tempKXXXXX`  #K represents the order of the sensors and XXXXX means the real tempture*1000

Issue a start/stop of the Fan
    | Message that starts/stops the fan:
    | :code:`fanon/fanoff` 

Issue a start/stop of the Heater
    | Message that starts/stops the heater:
    | :code:`heateron/heateroff`

Change the value of a parameter
    | Message that changes the value of a parameter
    | :code:`parachKXXXXX` #K represents the order of the parameters defined in the file of claudio's. XXXXX means the replaced parameter value. iF it is temperture then the real temperture * 1000. 
