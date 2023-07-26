# System Requirement Specification (SRS)

## Scope

### Terminology 

FR - functional requirement
RI - Risk
DT - Digital Twin 
PT - Physical Twin

## Risks

### Technical 
RI1 : The insulated box is not properly insulated

RI2 : Logging of the temperature measurements are inaccurate or represented temporally incorrect 

RI3 : The Current configuration of either the controller og the digital twin are not syncronized correctly or at all

RI4 : Container updates/failures causes some data-loss in the down time

### Cost 
RI5 : Electricity required to keep the heater and fan active are too high due to the usage of low-end hardware

RI6 : The cloud database and monitoring tools used in the design raises their prices increasing cloud costs 

### Programmatic
RI7 : The cloud database and monitoring tools used in the design goes out of service and will decomission the database on tools used by the Digital Twin 


## Requirements

### Functional Requirements

FR1 : The incubator shall be designed to heat fermented soybeans at just below 37 degrees celcius with at most a  $\pm$ 3 degree celcius margin of error

FR2 : The incubator shall be designed to detect whether the lid on the incubator is open or not. In case of an open lid, the box should not try to maintain a temperature of 37 degrees celcius

FR3 : The incubator shall be able to relay temperature measurements inside the insulated container

FR4 : The incubator shall be able to relay temperature measurements outside of the insulated container 

FR5 : A low level driver shall be able to turn on and off the heater via analog signals 

FR6 : A low level driver shall be able to turn on and off the fan via analog signals

FR7 : A message oriented middleware system must control the communication flow between a controller device and the digital twin 

FR8 : A message oriented middelware system must control the communication flow between a low level driver and the controller

FR9 : The Digital Twin must estimate the temperature inside the incubator with a 95% accuracy. 

FR10 : The temperature sensors inside and outside of the incubator should supply enough data to the digital twin, so that it can meet FR9

FR11: The Incubator shall be designed as such that a user may change between different heating strategies (MUST BE SPECIFIED FURTHER)

### Non-functional Requirements 

NFR1 : The controller should be the only component to supply data to the message oriented middleware and also recieve all data from the message oriented middleware 

## Stakeholders 

The stakeholders 

* DT operators 
* Incubator operators 

## Requirement Traceability Matrix 

| Project Name | | Business Area | |
|--------------|-|---------------|-|
| Project manager || Business Analysts lead ||
| QA lead || Target implementation date ||

| Req. id | FURBS category | Req. Description | Use-Case reference | Design document reference | Test case reference | User acceptance validation | comments |  
|---------|----------------|------------------|--------------------|---------------------------|---------------------|----------------------------|-------------|
| FR1 | F | Heat at temperature about 37 degrees |
| FR2 | F | Detect if the lid on the incubator is open |
| FR3 | F | 
| FR4 | F |
| FR5 | F |
| FR6 | F |
| FR7 | F |
| FR8 | F |
| FR9 | F |
| FR10| F |
| FR11| F |
| NFR1| R |

  
