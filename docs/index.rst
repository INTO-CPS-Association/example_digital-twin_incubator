

###########################################
INTO-CPS Digital Twin Case Study: Incubator
###########################################

This is a case study of an Incubator with the purpose of understanding the steps and processes involved in developing a digital twin system.
An incubator, or heater, is an insulated container with the ability to keep a temperature via heating but without active cooling.

The main novelity potential is the ability to answer what-if questions, which is somewhat general for digital twins.
The controller does not need any sophisticated model to work, but any other questions regarding the future behaviour of a system with possibly open loop control, will require a somewhat good model of what’s actually happening inside the box at the time the questions are asked.

Furthermore, the hope is that the approach used / created during this case study can be reused for other case studies.

***************
System Overview
***************
.. image:: images/system.png
    :align: center

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