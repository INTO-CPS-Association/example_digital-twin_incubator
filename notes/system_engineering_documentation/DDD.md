# Detailed Design Document

## Preliminary design
The diagram represensts the current design for the incubator and serves as a basis for how the system is designed aswell as the communication flow in the system.

![Alt text](../../software/docs/images/L1_main_dependencies.svg)
## Detailed design
### System-wide design decisions
**RabbitMQ**

RabbitMQ is the chosen message oriented middleware, which is used as the communications manager between all the different services that operates between the digital twin and the physical twin. 

It uses *topic* based communication to route messages to the right queue. This helps the system to achive a low coupling and a higher degree of scalability.

**Influx**

InfluxDB is chosen as the database provider, since it opperates primarily by Time series indexing. This helps the system to keep a historical timeline of events that has transpired on the physical twin, so that the digital twin can get an accurate understanding of when each event has taken place. 

**Docker**

Each and every service in the system is setup as their own containers, all communicating on a shared network, this allows the inidiviual services to be deployed on the same machine, but in seperate containers. 


### System components

The Plant contains a handful of component which can be seen in the following diagram 

![Incubator components](../../figures/system.svg)

**Plant**

* Heater : RepRap PCB Heat bed MK2a
* Fan : SUNON fan 24V
* Temperatur sensor : DS18S20
* Content : Soybeans (typically)

**Controller**

* Controller CPU : Raspberry Pi 4 Model B - 4 GB
* Controller memory : Rasberry Pi 6GB Micro SD - Class A1 - with NOOBS
* Controller Power Supply : Raspberry Pi USB-C power supply 5V 3A
* Controller UI : Rasbperry Pi 7" touchscreen display with SmartiPi Touch 2 Casing
* Controller input : USB micro SD cardreader

Legend:

ControllerOptimizer
- Fine tunes the controllers parameters based on the simulation results

SelfAdaptationManager
- Can react to anomalies detected in the physical plant and recalibrate in regards to the changes that has happened

KalmanFilter
- Anomaly detector based on full system states

InfluxDataRecorder
- Records data based on Topics related to time series data and stores them in the InfluxDB Database

InfluxDB
 - Time series data store that contains all the data stored recorded by the 

Calibrator
- Based on the real time data stored in InfluxDB, the calibrator can estimate the parameter values of the plant model

PhysicalTwinSimulator
-  Simulates the behaviour of the physical twin based on the real time data stored in InfluxDB

PlantModel
- A Model describing the properties and behaviour of the incubator chamber

ControllerModel
- A model describing the properties and behaviour of the incubator controller

PlantSimulator
- The container that runs the actual simulation of the running model of the incubator

### Sequence diagram
![Alt text](../../software/docs/images/self_adaptation_sequence.svg)

## Interface design
## Modules
## Specification