###########################################
INTO-CPS Digital Twin Case Study: Incubator
###########################################

This is a case study of an Incubator with the purpose of understanding the steps and processes involved in developing a digital twin system.
An incubator, or heater, is an insulated container with the ability to keep a temperature via heating but without active cooling.

***************
System Overview
***************

.. image:: images/system.png
    :align: center
    :alt: System

The system consists of:

- A styrofoam box in order to have an insulated container.
- A heat source to heat up the content within the styrofoam box.
- A fan to distribute the heating within the box
- A temperature sensor to monitor the temperature within the box
- A temperature Sensor to monitor the temperatur:e outside the box
- A controller to communicate with the digital t:win, actuate the heat source and the fan and read sensory information from the temperature sensors.

.. toctree::
    :maxdepth: 3
    :caption: Content
    :hidden:

    system_overview    
    hardware
    experiments
