This folder contains the code that makes the digital twin possible.

# Directory Structure

```
├───cli -- Contains code to communicate with the running DT components.
├───digital_twin -- Code that forms the digital twin.
├───docs -- Documentation.
├───incubator -- Code that implements the physical twin
├───integration_tests -- Code to run tests that involve settup and running scenarios with the DT components.
├───mock_plant -- Code setting up the local virtual incubator plant.
├───old_software -- Old code that is still being organized
└───startup -- Code that allows starting and stopping the DT components.
```

# Cloning this repo

When cloning this repo, don't forget to initialize the ![submodules](https://git-scm.com/book/en/v2/Git-Tools-Submodules).

# Running the Unit Tests

## First-time setup
1. Open terminal in this folder.
2. Optional: create a virtual environment: `python -m venv venv`
3. Optional: activate the virtual environment (there are multiple possible activate scripts. Pick the one for you command line interface.): 
   1. Windows Powershell:`.\venv\Scripts\Activate.ps1` 
   2. Linux/Mac: `source venv/bin/activate`
4. Recommended: install pip wheel: `pip install wheel`
5. Install dependencies:
   1. `pip install -r ./requirements.txt`.


## After first time setup

See script [./run_tests.ps1](./run_tests.ps1) for more details on which environment variables to set.
Configure your IDE accordingly.

# Starting the DT framework

Follow the instructions in [README.md](./startup/README.md)

# Running Integration Tests

Make sure you can successfully start the DT framework and run the unit tests before attempting to run the integration tests.

The script [run_integration_tests.ps1](./run_integration_tests.ps1) contains the instructions.

