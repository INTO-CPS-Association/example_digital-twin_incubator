# Software

This directory contains all things code related.

```
├───cli -- Contains code to communicate with the running DT components.
├───digital_twin -- Code that forms the digital twin.
├───incubator -- Code that implements the physical twin and models
├───integration_tests -- Code to run integration tests.
├───mock_plant -- Code setting up the local virtual incubator plant.
└───startup -- Code to start and stop the DT services.
```

## Running the Digital Twin Locally

### First-time Setup
1. Open terminal in this folder.
2. (Optional) Create a virtual environment: `python -m venv venv`
3. (Optional) Activate the virtual environment (there are multiple possible activate scripts. Pick the one for you command line interface.): 
   1. Windows Powershell:`.\venv\Scripts\Activate.ps1` 
   2. Linux/Mac: `source venv/bin/activate`
4. (Optional) Install pip wheel: `pip install wheel`
5. Install dependencies:
   1. `pip install -r ./requirements.txt`
6. Make sure the PYTHONPATH [environment variable](https://www3.ntu.edu.sg/home/ehchua/programming/howto/Environment_Variables.html) contains the [incubator](./incubator/) folder: 
   1. (Powershell) `$Env:PYTHONPATH = "incubator"`

### After First-time Setup: Starting the DT Framework

1. Create a [startup.conf](./startup.conf) file in the folder of this readme file. Copy [example_startup.conf](./example_startup.conf) and change if needed. You should not need to change anything for running the DT locally.
2. Follow the instructions in [./startup/README.md](./startup/README.md)
3. Recommended: [Run the unit tests](#running-unit-tests)
4. Recommended: [Run the integration tests](#running-integration-tests)

### Running Unit Tests

Make sure you can successfully [start the DT framework](#after-first-time-setup-starting-the-dt-framework)

To run the unit tests, open a terminal in the directory of this readme file, and
1. Activate virtual environment
2. If using powershell, run [./run_tests.ps1](./run_tests.ps1)
3. Otherwise:
   1. Set environment variable CLIMODE = "ON"
   2. Set environment variable PYTHONPATH = "incubator"
   3. Run tests: `python -m unittest discover -v incubator/tests -p "*.py"`

### Running Integration Tests

Make sure you can successfully [start the DT framework](#after-first-time-setup-starting-the-dt-framework) and [run the unit tests](#running-unit-tests) before attempting to run the integration tests.

The script [run_integration_tests.ps1](./run_integration_tests.ps1) contains the instructions.

## System Architecture

Read the documentation in [./docs/README.md](./docs/README.md)
