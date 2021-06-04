# Notes for Research Roadmap

Tasks:
- [x] Read basics of concepts
  - [x] traceability (0.5h)
  - [x] configuration management (0.5h)
  - [x] data migration (0.5h)
  - [x] contract based design (0.5h)
  - [x] complex event processing (0.5h)
  - [x] experimental frame (0.5h)
  - [x] run-time monitoring (0.5h)
  - [x] source code repository management (0.5h)
  - [x] continuous integration
- [ ] Collect some recent papers on them:
  - [ ] traceability (0.5h)
  - [ ] configuration management (0.5h)
  - [ ] data migration (0.5h)
  - [ ] contract based design (0.5h)
  - [ ] complex event processing (0.5h)
  - [ ] experimental frame (0.5h)
  - [ ] run-time monitoring (0.5h)
  - [ ] source code repository management (0.5h)
  - [ ] continuous integration


## traceability (e.g., into-cps OSLC tuples)

### Gotel1994 - An analysis of the requirements traceability problem

> Requirements traceability refers to the ability to describe and follow the life of a requirement, in both a forwards and backwards direction.

> Numerous techniques have been used for providing RT, including: cross referencing schemes [161]; keyphrase dependencies [28]; templates [27]; RT matrices [9]; matrix sequences [4]; hypertext [32]; integration documents [36]; assumption-based truth maintenance networks [53]; and constraint networks [2]. 
> These differ in the quantity and diversity of information they can trace between, in the number of interconnections they can control between information, and in the extent to which they can maintain RT when faced with ongoing changes to requirements.

A RQ might be:
What is the best way to handle the requirements of DTs? If DTs are expected to be long lived, so it is important to have a clear record of changes made, and why they were made.

> This finding implies that both eager and lazy generation of project information is required. By eager, we mean whilst engaged in aspects of RS production

## configuration management

### Conradi1998 - Version models for software configuration management

Idea: we should try to apply ASP (or something else), to do configuration management of Digital Twins. THis is similar to the challenge in robotics, where different robots collaborate to accomplish a particular task, so they must find out what they can do according to each own's skills.

> Different approaches have been developed to accommodate changes to the database schema. In the case of schema evolution, only the current version of the schema is valid, and all data must be converted (in lazy or eager mode) in order to maintain the consistency of the database.

## data migration

Wikipedia

## contract based design

### Meyer1992 - Applying 'design by contract'

They nicely summarize the application of design by contract to OO programming.

Nice to study how to apply these to digital twins.

## complex event processing

### Cugola2012 - Processing flows of information: From data stream to complex event processing

> Examples of IFP applications come from the most disparate fields. In environmental monitoring, users need to process data coming from sensors deployed in the field to acquire information about the observed world, detect anomalies, or predict disasters as soon as possible [Broda et al. 2009; Event Zero 2010a]. Similarly, several financial applications require a continuous analysis of stocks to identify trends [Demers et al. 2006]. Fraud detection requires continuous streams of credit card transactions to be observed and inspected to prevent frauds [Schultz-Moeller et al. 2009]. To promptly detect and possibly anticipate attacks to a corporate network, intrusion detection sys- tems have to analyze network traffic in real-time, generating alerts when something unexpected happens [Debar and Wespi 2001]. RFID-based inventory management per- forms continuous analysis of RFID readings to track valid paths of shipments and to capture irregularities [Wang and Liu 2005]. Manufacturing control systems often re- quire anomalies to be detected and signalled by looking at the information that describe how the system behaves [Lin and Zhou 1999; Park et al. 2002].

> The broad spectrum of applications domains that require information flow process- ing in this sense explains why several research communities focused their attention to the IFP domain, each bringing its own expertise and points of view, but also its own vocabulary. The result is a typical **Tower of Babel syndrome**, which generates mis- understandings among researchers that negatively impact the spirit of collaboration required to advance the state of the art [Etzion 2007].

Seems that this is an important component of the DT.

Example event:
> a fire is detected when three different sensors located in an area smaller than 100 m2 report a temperature greater than 60◦C, within 10 s, one from the other.

> Whatever language is used, subscriptions may refer to single events only [Aguilera et al. 1999] and cannot take into account the history of already received events or relationships between events. To this end, CEP systems can be seen as an extension to traditional publish-subscribe, which allow subscribers to express their interest in composite events. 

They highlight an interesting issue:
if these systems are all real time and whatnot, how to we deal with transactions? Rollback? That can't be the case, because we're dealing with physical systems.

#### Possible interesting research directions:

> Related with the issue of expressiveness is the ability to support uncertainty in data and rule processing. As we have seen, a single system supports it among those we surveyed, but we feel this is an area that requires more investigation, since it is something useful in several domains.

> Along the same line, we noticed how the ability for a rule to programmatically manipulate the set of deployed rules by adding or removing them is common in active databases but is rarely offered by more recent IFP systems. Again, we think that this is potentially very useful in several cases and should be offered to increase the expressiveness of the system

## experimental frame

### Denil2017 - The experiment model and validity frame in M&S

## run-time monitoring (LTL, metric LTL, etc...)

Very technical on properties.
We can probably take an existing tool on LTL, combine it with a complex event processing engine, and get decent functionality in practice.

## Continuous integration

### Fowler2006 - Continuous integration

## Combination of above with digital twin

### Zhou2019a - Digital twin framework and its application to power grid online analysis

They present a DT for power system analysis.

The architecture contains a complex event processing tool.
