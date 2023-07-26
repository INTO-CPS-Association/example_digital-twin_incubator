# Detailed Design Document

## Preliminary design
THe diagram represensts the current design for the incubator and serves as a basis for how the system is designed aswell as the communication flow in the system.

![Alt text](../../software/docs/images/L1_main_dependencies.svg)
## Detailed design
### System-wide design decisions
RabbitMQ

Influx

Other technologies?
### System components
Plant
Controller
Legend:

ControllerOptimizer

SelfAdaptationManager

KalmanFilter

InfluxDataRecorder

InfluxDB

Calibrator

PlantSimulator

PlantModel

ControllerModel

PhysicalTwinSimulator

### Sequence diagram
![Alt text](../../software/docs/images/self_adaptation_sequence.svg)

## Interface design
## Modules
## Specification