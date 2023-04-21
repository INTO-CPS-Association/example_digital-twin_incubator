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
