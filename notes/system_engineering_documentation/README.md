# System Engineering Documentation

## Terminology 

FR - functional requirement
RI - Risk
DT - Digital Twin 

## Risks

### Technical 
RI1 : insulated box is not insulated

RI2 : Logging of temperature messuraments are inaccurate or represented temporally incorrect 

RI3 : Current configuration of either controller og digital twin are not syncronized 

RI4 : Container updates/failures causes some data loss in down time

### Cost 
RI5 : Electricity required to keep heater and fan active are high due to low-end hardware


## Requirements

### Functional Requirements

FR1 : The incubator shall be designed to heat fermented soybeans

FR2 : The incubator shall be able to return temperatur measurements inside the insulated container

FR3 : The incubator shall be able to return tempertur measurements outside of the insulated container 

FR4 : A low level driver shall be able to turn on and off the heater

FR5 : A low level driver shall be able to turn on and off the fan

FR6 : A message oriented middleware system must control the communication flow between a controller device and the digital twin 

FR7: A message oriented middelware system must control the communication flow between a low level driver and the controller


## Stakeholders 

* DT operators 
* Incubator operators 
