***************
System Overview
***************

The communication system setup in as depicted in :ref:`communication_system_setup`.
All communication goes through the RabbitMQ server, even the communication between the controller and the IO layer on the Raspberry Pi.
This ensures a completely opaque view of all hardware communication. Thus, if the controller wants to read a temperature it publishes a `read temperature` message. 
The IO layer will receive this message and issue a read on the GPIO. Once the reading is finished, then the IO layer will publish a `temperature` message, which the controller receives.
Anyone else interested in this communication, such as the digital twin, can listen to all of this communication as well.

.. figure:: images/system_setup.png
    :align: center
    :name: communication_system_setup
    
    Communication System Setup

.. include:: communication_protocol.rst
