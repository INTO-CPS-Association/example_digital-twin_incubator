********
Hardware 
********

Hardware Elements
#################
-   3 temperature sensors of the type DS18S20
-   | 1 heat bed of the type RepRap PCB Heat bed MK2a (improved design)
    | Dimensions (Heat Bed): 200mm x 200mm
    | Resistance: 0.9 - 1.1 Ohms 
    | Operating voltage: 12 Volts
    | Operating current: 11 - 13 Amps
-   | 1 Fan 24V 92x25 B 87,4m³/h 34dBA - https://elektronik-lavpris.dk/files/sup2/EE92252B1-A99_D09023340G-00.pdf - https://elektronik-lavpris.dk/p122514/ee92252b1-a99-fan-24v-92x25-b-874m-h-34dba/
-   | Raspberry Pie starter kit
    | Raspberry Pi 4 Model B - 4 GB - https://www.raspberrypi.org/documentation/hardware/raspberrypi/bcm2711/rpi_DATA_2711_1p0_preliminary.pdf
    | 6GB Micro SD - Class A1 - Med NOOBS
    | Officiel Raspberry Pi USB-C Strømforsyning – EU – 5V 3A - Sort
    | Officiel Raspberry Pi 7" Touchscreen Display
    | SmartiPi Touch 2 - Case til Raspberry Pi 7" Touchscreen Display 
    | USB Micro SD Kortlæser
-   | Thermo box - Climapor thermokasse m/låg t/Eurokasse 54,5x35x18 cm
-   | Custom Electronics 

.. warning:: 
    Add custom electronics information

Raspberry Pi GPIO connections
#############################
| GPIO 12: PWM Heater 
| GPIO 13: PWM Fan
| GPIO 4: 1-wire temperature sensors

Temperature Sensor Mapping
==========================
In order to read a temperature from the temperature sensors multiple IDs can be found in : :code:`/sys/bus/w1/devices/`.
So to read a value from a sensor, one can do: :code:`cat /sys/bus/w1/devices/10-0008039ad4ee/w1_slave`.

Each ID in the devices folder correspond to a particular sensor. Follow the wires of the temperature sensors and you will find a paper label with a number on it.
The ID to number mapping is:

.. csv-table:: ID to Sensor Number Mapping
   :header: "ID", "Sensor Number"

       "10-0008039ad4ee", "1"
       "10-0008039b25c1", "2"
       "10-0008039a977a", "3"