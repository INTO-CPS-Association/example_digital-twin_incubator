# Example Digital Twin: The Incubator

This is a case study of an Incubator with the purpose of understanding the steps and processes involved in developing a digital twin system.
This incubator is an insulated container with the ability to keep a temperature and heat, but not cool.

To understand what a digital twin is, we recommend you read/watch one or more of the following resources:
- Feng, Hao, Cláudio Gomes, Casper Thule, Kenneth Lausdahl, Alexandros Iosifidis, and Peter Gorm Larsen. “Introduction to Digital Twin Engineering.” In 2021 Annual Modeling and Simulation Conference (ANNSIM), 1–12. Fairfax, VA, USA: IEEE, 2021. https://doi.org/10.23919/ANNSIM52504.2021.9552135.
- [Claudio's presentation at Aarhus IT](https://videos.ida.dk/media/Introduction+to+Digital+Twin+Engineering+with+Cl%C3%A1udio+%C3%82ngelo+Gon%C3%A7alves+Gomes%2C+Aarhus+Universitet/1_7r1j05g8/256930613)

# Contents
- [Example Digital Twin: The Incubator](#example-digital-twin-the-incubator)
- [Contents](#contents)
- [About this Document](#about-this-document)
- [Overview of the Documentation](#overview-of-the-documentation)
  - [Searching](#searching)
- [Terminology](#terminology)
- [Our Concept of Digital Twin](#our-concept-of-digital-twin)
- [The Incubator Physical Twin](#the-incubator-physical-twin)
  - [CAD Model](#cad-model)
  - [Dynamic Models](#dynamic-models)
  - [Running The Incubator Physical Twin](#running-the-incubator-physical-twin)
- [The Digital Twin](#the-digital-twin)
  - [Running the Digital Twin](#running-the-digital-twin)
    - [First-time Setup](#first-time-setup)
    - [After First-time Setup: Starting the DT Framework](#after-first-time-setup-starting-the-dt-framework)
    - [Running Unit Tests](#running-unit-tests)
    - [Running Integration Tests](#running-integration-tests)
- [Diagnosing Startup Errors](#diagnosing-startup-errors)
  - [RabbitMQ Setup](#rabbitmq-setup)
  - [InfluxDB Setup](#influxdb-setup)
- [Repository Maintenance Instructions](#repository-maintenance-instructions)



# About this Document

**Goal:** The goal of this document is to provide users with a basic overview of the digital twin incubator and enabled them to run it on their computers.

**Audience:** This documentation is targeted at users who are acquainted with running programs from the command line and are able to install [python](https://www.python.org/) and run python scripts.

# Overview of the Documentation

The documentation is all contained into a single document for simplicity and ease of maintenance.
If the user wishes to see the documentation in some other format then we recommend cloning this repository and using [Pandoc](https://pandoc.org/) to convert the documentation into another format.

## Searching

Searching the documentation can be done by using the browser search function or using Github's search feature on top of the screen.

# Terminology

- **Plant** -- we use the term in the traditional control systems sense. The plant refers to the box contents, the heater, the sensor, and the fan. Basically it is the stuff that the controller is sensing and actuating on.
- **Controller** -- To control this responsibility is to decide when to turn on/off the heater.
- **Low Level Driver** --- This refers to the component that decouples the controller from the plant. It forms a layer that abstracts away from the details of how the actuators and sensors work and enables us to run the whole system locally on a computer without the need to connect to a real plant.

# Our Concept of Digital Twin

A digital twin is a software system that supports the operation of a cps (called the physical twin).
So the following documentation describes the physical twin first and then the digital twin.

# The Incubator Physical Twin

The overall purpose of the system is to reach a certain temperature within a box and keep the temperature regardless of content.

![Incubator](figures/system.svg)

The system consists of:
- 1x Styrofoam box in order to have an insulated container.
- 1x heat source to heat up the content within the Styrofoam box.
- 1x fan to distribute the heating within the box
- 2x temperature sensor to monitor the temperature within the box
- 1x temperature Sensor to monitor the temperature outside the box
- 1x controller to actuate the heat source and the fan and read sensory information from the temperature sensors, and communicate with the digital twin.

## CAD Model

A .obj file is available at: [figures/incubator_plant.obj](figures/incubator_plant.obj).

![CAD Model](./figures/incubator_plant.png)

Ongoing development of the cad model is at 
[incubator](https://www.tinkercad.com/things/ls1YolyX1fc-incubatorv20230429)

## Dynamic Models

TODO

## Running The Incubator Physical Twin

On the raspberry pi: 
1. Start the [low_level_driver_server.py](software/incubator/physical_twin/low_level_driver_server.py)
   ```powershell 
   PS software> python -m incubator.physical_twin.low_level_driver_server
   ```
2. Start the controller you wish to use. For example the [start_controller_physical.py](software/startup/start_controller_physical.py) is:
   ```powershell 
   PS software> python -m startup.start_controller_physical
   ```

# The Digital Twin

The DT follows a service based architecture, with different services communicating with each other via a [RabbitMQ message exchange](https://www.rabbitmq.com/) running on a [docker](https://www.docker.com/products/docker-desktop) container.
Each service is started with a python script, and most services refer to [software/startup.conf](software/startup.conf) for their configuration.

The code that starts the services is in [software/startup](software/startup).
It is possible to start all services from the same script [software/startup/start_all_services.py](software/startup/start_all_services.py) or each service individually.

The services (and their starting scripts) currently implemented are:
- [incubator_realtime_mockup](software/startup/start_incubator_realtime_mockup.py) -- implements a real time plant simulation mockup so that the whole digital twin system can be run locally on any computer without the need to connect to an external physical twin. When using a real physical twin this service is not started.
- [low_level_driver_mockup](software/startup/start_low_level_driver_mockup.py) -- This instantiates a low level driver service that is wired to work with a real time plant simulator mockup. When using a real physical twin this service is not started.
- [influx_data_recorder](software/startup/start_influx_data_recorder.py) -- the service listens to a particular topic from RabbitMQ records the messages into the time series database [InfluxDB](https://portal.influxdata.com/downloads/)
- [plant_kalmanfilter](software/startup/start_plant_kalmanfilter.py) -- This service estimates the full state of the system and is used as a basis for anomaly detection.
- [plant_simulator](software/startup/start_plant_simulator.py) -- The service can run simulations based on the data from the time series database with different conditions for the plant model.
- [simulator](software/startup/start_simulator.py) -- This service can run simulations of the controller and plant system from data based on the data from the time series databases with different conditions.
- [calibrator](software/startup/start_calibrator.py) -- The service can use data from the time series database to estimate the parameters of the plant model.
- [controller_physical](software/startup/start_controller_physical.py) -- this service implements the controller.
- [supervisor](software/startup/start_supervisor.py) -- This service can periodically retune the controller.
- [self_adaptation_manager](software/startup/start_self_adaptation_manager.py) -- the service implements the self-adaptation which checks whether the physical characteristics of the plant have changed and can trigger a recalibration as well as controller tuning when that happens.

## Running the Digital Twin

It is possible to run the digital twin on our computer, with or without a connection to the physical twin.

*You're advised to read carefully all documentation before acting on any instruction.*

### First-time Setup
1. Open terminal in [software](software).
2. (Optional) Create a virtual environment: `python -m venv venv`
3. (Optional) Activate the virtual environment (there are multiple possible activate scripts. Pick the one for your terminal.): 
   1. Windows Powershell:`.\venv\Scripts\Activate.ps1` 
   2. Linux/Mac: `source venv/bin/activate`
4. (Optional) Install pip wheel: `pip install wheel`
5. Install dependencies:
   1. `pip install -r ./requirements.txt`
6. Install [docker](https://www.docker.com/products/docker-desktop) installed (see [Docker Homepage](https://docs.docker.com/desktop/))


### After First-time Setup: Starting the DT Framework

1. Inspect the [startup.conf](./software/startup.conf) in this folder. You should not need to change anything for running the DT locally.
2. Make sure docker is running. 
3. Run
   ```bash
   software$ python -m startup.start_all_services
   ```
4. After starting all services successfully, the controller service will start producing output that looks like the following:
   ````
   time           execution_interval  elapsed  heater_on  fan_on   room   box_air_temperature  state 
   19/11 16:17:59  3.00                0.01     True       False   10.70  19.68                Heating
   19/11 16:18:02  3.00                0.03     True       True    10.70  19.57                Heating
   19/11 16:18:05  3.00                0.01     True       True    10.70  19.57                Heating
   19/11 16:18:08  3.00                0.01     True       True    10.69  19.47                Heating
   19/11 16:18:11  3.00                0.01     True       True    10.69  19.41                Heating
   ````
5. Login to http://localhost:8086/ (or more generally http://[Influxdb_IP]:8086/) to see the influxdb management page, were you can create dashboards to see the data produced by the incubator. The login details are:
   - user=`incubator`
   - password=`incubator`
6. Login http://localhost:15672/ to see the RabbitMQ management page. The login details are:
   - user=`incubator`
   - password=`incubator`
7. See [Diagnosing Startup Errors](#diagnosing-startup-errors) in case you encounter problems
8. Recommended: [Run the unit tests](#running-unit-tests)
9. Recommended: [Run the integration tests](#running-integration-tests)

### Running Unit Tests

Make sure you can successfully [start the DT framework](#after-first-time-setup-starting-the-dt-framework)

To run the unit tests, open a terminal in [software](software), and
1. Activate virtual environment
2. If using powershell, run [./run_tests.ps1](./software/run_tests.ps1)
3. Otherwise:
   1. Set environment variable `CLIMODE = "ON"`
   2. Run tests: `python -m unittest discover -v incubator/tests -p "*.py"`

### Running Integration Tests

Make sure you can successfully [start the DT framework](#after-first-time-setup-starting-the-dt-framework) and [run the unit tests](#running-unit-tests) before attempting to run the integration tests.

The script [run_integration_tests.ps1](./software/run_integration_tests.ps1) contains the instructions.

# Diagnosing Startup Errors

If any errors show up during the startup process, check that the RabbitMQ server and InfluxDB are being correctly started. 

The following instructions were used to configure these services in the first time and may help you test them:

## RabbitMQ Setup

[Rabbitmq README](software/incubator/communication/installation/README.md)

## InfluxDB Setup

[Influxdb README](software/digital_twin/data_access/influxdbserver/README.md)

# Repository Maintenance Instructions

We make extensive use of README.md files. Please read them and keep them up to date.

General guidelines:
1. Run the tests as often as possible.
2. Create tests as much as possible. If the tests are long running, such as calibrations and optimizations, create a version of the test that runs faster (e.g., on a subset of data) when running the tests from the command line. See [example_test.py](./software/incubator/tests/example_test.py).
3. Create code that is testable.
4. Ask for code reviews (code readable by at least two people is more likely readable by a third)
5. Organize and document datasets and experiments.
6. Beware of large datasets. Host them elsewhere if needed, but include a short version of the dataset in the repository.
7. Don't be afraid of reorganizing the code and repo if you think that's necessary. This is an ongoing learning process for everyone. Discuss with Casper, Kenneth, or Claudio before doing so if you're not sure.
8. We shy away from branches except when they add a substantial amount of functionality. Commit and push responsibly to the main branch, that is, always make sure that:
   1. That all tests pass (unit tests and integration tests).
   2. That new code is documented and tested.
   3. That documentation links are not broken. Use for example, [markdown-link-check](https://github.com/tcort/markdown-link-check) to check all md files for broken links:
      1. `Get-ChildItem -Include *.md -Recurse | Foreach {markdown-link-check --config .\markdown_link_check_config.json $_.fullname}`
9.  Much more on https://github.com/HugoMatilla/The-Pragmatic-Programmer
