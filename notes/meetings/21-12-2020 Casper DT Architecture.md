# Casper DT Architecture


Related tecnologies:
- service oriented architecture
  - https://en.wikipedia.org/wiki/Service-oriented_architecture

Interesting principles from https://en.wikipedia.org/wiki/Service-oriented_architecture#Principles
- Standardized service contract - Services adhere to a standard communications agreement, as defined collectively by one or more service-description documents within a given set of services.
- Service reference autonomy (an aspect of loose coupling) - The relationship between services is minimized to the level that they are only aware of their existence.
- Service location transparency (an aspect of loose coupling) - Services can be called from anywhere within the network that it is located no matter where it is present.
- Service longevity - Services should be designed to be long lived. Where possible services should avoid forcing consumers to change if they do not require new features, if you call a service today you should be able to call the same service tomorrow.
- Service abstraction - The services act as black boxes, that is their inner logic is hidden from the consumers.
- Service autonomy - Services are independent and control the functionality they encapsulate, from a Design-time and a run-time perspective.
- Service statelessness - Services are stateless, that is either return the requested value or give an exception hence minimizing resource use.
- Service granularity - A principle to ensure services have an adequate size and scope. The functionality provided by the service to the user must be relevant.
- Service normalization - Services are decomposed or consolidated (normalized) to minimize redundancy. In some, this may not be done. These are the cases where performance optimization, access, and aggregation are required.
- Service composability - Services can be used to compose other services.
- Service discovery - Services are supplemented with communicative meta data by which they can be effectively discovered and interpreted.
- Service reusability - Logic is divided into various services, to promote reuse of code.
- Service encapsulation - Many services which were not initially planned under SOA, may get encapsulated or become a part of SOA.


Questions:
- Is rabbitmq the appropriate way? 
  - How does it enable discovery?
  - How do we transmit lots of data between services using rabbitmq?
- How do we represent the data? There has to be some standard format for it to be sent between services.
- How do we deal with DEVOps stuff? Updating elements, etc...
- What are the non-functional requirements?
  - CT: Authentication is very different from company to company
  - CT: We cannot do anything reasonable about this.
- Are they a concern for us?
- Is the kafka the best framework for communication with DTs?
  - Seems pretty good: https://www.kai-waehner.de/blog/2020/03/25/architectures-digital-twin-digital-thread-apache-kafka-iot-platforms-machine-learning/

Related work:
- https://www.eclipse.org/ditto/intro-overview.html
  - https://www.eclipse.org/ditto/intro-hello-world.html
  - Seems to facilitate authentication.
  - We never thought about authentication here.
  - Uses http protocols to interact with "Things".
  - Has mechanisms to list all Things.
  - More info in https://github.com/svaidyans/Digital_Twin#eclipse-ditto-implementation
- https://prometheus.io/
  - Monitoring
- https://grafana.com/
  - Plotting
- From https://github.com/svaidyans/Digital_Twin
- There are lots of IOT frameworks.
- https://kafka.apache.org/intro
  - Storing data.
  - May also be used to implement communication? 
- https://www.youtube.com/watch?v=Q3eKPEVwNVY&ab_channel=KaiW%C3%A4hner
  - Also here: https://www.kai-waehner.de/blog/2020/03/25/architectures-digital-twin-digital-thread-apache-kafka-iot-platforms-machine-learning/
  - They use kafka as basis for DT.


Casper will play with Kafka:
- Can it be used for what-if analysis scenario?
  - Persist historical data of system
  - A service (e.g., the DT Master) can send control (non persistent data) data between services (e.g., ask to start a what-if simulation)?
- Send notes to Claudio and Fateme.

Casper:
- We will need data connections to import data from any other DB into a kafka DB.
- We argue for kafka because it's a good enough tool for communication.

