# System Overview

We use the [C4 Model](https://c4model.com/) to document the software architecture.

![L0_Communication](images/L0_Communication.svg)

All communication goes through the RabbitMQ server, even the communication between the Controller and Plant.
The Controller communicates with the Plant by listening and sending RabbitMQ messages to the [low_level_driver_server.py](../incubator/physical_twin/low_level_driver_server.py).

Anyone else interested in this communication, such as the digital twin, can listen to it as well.

## Self-Adaptation

The most complex behavior is the self-adaptation, as it involves most implemented DT components.

This is introduced in the following paper, which we recommend you read:
- Feng, Hao, Cláudio Gomes, Santiago Gil, Peter H. Mikkelsen, Daniella Tola, Peter Gorm Larsen, and Michael Sandberg. “Integration Of The Mape-K Loop In Digital Twins.” In 2022 Annual Modeling and Simulation Conference (ANNSIM), 102–13. San Diego, CA, USA: IEEE, 2022. https://doi.org/10.23919/ANNSIM55834.2022.9859489.
- *Note that diagrams in the paper are likely outdated. Updated diagrams are shown below*

The main components and their dependencies are:

![L1_main_dependencies](images/L1_main_dependencies.svg)

Legend:
- [MQ] - Communication happens via RabbitMQ messages.
- [API] - Communication happens via method call.

The following shows the main stages involved in a self-adaptation:

![MAPEK_Loop](images/MAPEK_Loop.svg)

In particular, these are followed by the SelfAdaptationManager:

![self_adaptation_state_machine](images/self_adaptation_state_machine.svg)


The following diagram shows the main interactions between the main entities that participate in the self-adaptation process. It is assumed that an anomaly has occurred due to the lid being open.


![self_adaptation_sequence](images/self_adaptation_sequence.svg)


## Hardware Overview

Hardware Elements
- 3 temperature sensors of the type DS18S20
- 1 heat bed of the type RepRap PCB Heat bed MK2a (improved design)
  - Dimensions (Heat Bed): 200mm x 200mm
  - Resistance: 0.9 - 1.1 Ohms 
  - Operating voltage: 12 Volts
  - Operating current: 11 - 13 Amps
- 1 Fan 24V 92x25 B 87,4m³/h 34dBA - https://elektronik-lavpris.dk/files/sup2/EE92252B1-A99_D09023340G-00.pdf - https://elektronik-lavpris.dk/p122514/ee92252b1-a99-fan-24v-92x25-b-874m-h-34dba/
- Raspberry Pie starter kit
  - Raspberry Pi 4 Model B - 4 GB - https://www.raspberrypi.org/documentation/hardware/raspberrypi/bcm2711/rpi_DATA_2711_1p0_preliminary.pdf
  - 6GB Micro SD - Class A1 - Med NOOBS
  - Officiel Raspberry Pi USB-C Strømforsyning – EU – 5V 3A - Sort
  - Officiel Raspberry Pi 7" Touchscreen Display
  - SmartiPi Touch 2 - Case til Raspberry Pi 7" Touchscreen Display 
  - USB Micro SD Kortlæser
- Thermo box - Climapor thermokasse m/låg t/Eurokasse 54,5x35x18 cm
- Custom Printed Circuit Board Electronics. You can find more information [here](./electronics/doc/doc.pdf).

### Raspberry Pi GPIO connections
- GPIO 12: PWM Heater 
- GPIO 13: PWM Fan
- GPIO 4: 1-wire temperature sensors

### Temperature Sensor Mapping
In order to read a temperature from the temperature sensors multiple IDs can be found in `/sys/bus/w1/devices/`.

So to read a value from a sensor, one can do: `cat /sys/bus/w1/devices/10-0008039ad4ee/w1_slave`.

Each ID in the `/sys/bus/w1/devices` folder correspond to a particular sensor. Follow the wires of the temperature sensors, and you will find a paper label with a number on it.
The ID to number mapping is:

ID to Sensor Number Mapping:

| ID              | Sensor Number |
|-----------------|:-------------:|
| 10-0008039ad4ee |       1       |
| 10-0008039b25c1 |       2       |
| 10-0008039a977a |       3       |
