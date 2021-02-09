This folder contains the code that makes the digital twin possible.

# Directory Structure

```
├───cli -- Contains code to communicate with the running DT components.
├───communication -- Contains code to establish the communication layer between physical twin and digital twin.
├───digital_twin -- Code that forms the digital twin.
├───docs -- Documentation.
├───integration_tests -- Code to run tests that involve settup and running scenarios with the DT components.
├───mock_plant -- Code setting up the local virtual incubator plant.
├───old_software -- Old code that is still being organized
├───incubator -- Code that implements the physical twin
├───startup -- Code that allows starting and stopping the DT components
└───tests -- Unit that exercise code on which the DT components depend.
```

# Running the Unit Tests

## First-time setup
1. Open terminal in this folder.
2. Optional: create a virtual environment: `python -m venv venv`
3. Optional: activate the virtual environment (there are multiple possible activate scripts. Pick the one for you command line interface.): 
   1. Windows Powershell:`.\venv\Scripts\Activate.ps1` 
   2. Linux/Mac: `source venv/bin/activate`
4. Install dependencies:
   1. `pip install -r ./requirements.txt`.
5. Set the environment variable `CLIMODE` to `ON`, so that plotting is suppressed.
   1. Windows Powershell: `$Env:CLIMODE = "ON"`
6. Use Unittest to run the tests.
   1. Example: `python -m unittest discover tests -p '*.py'`

## After first time setup

Follow the above instructions, skipping the installation of the dependencies.
See script [./run_tests.ps1](./run_tests.ps1) for more details.

# Creating Unit Tests

Follow the example of [./tests/example_test.py](./tests/example_test.py)

Each test should correspond to one experiment, and each experiment should be targeted at answering one question.

Commit the tests in a way that they can be run automatically and quickly (use the `self.cli_mode`).
If `self.cli_mode` is true:
1. Plotting should be avoided.
2. Optimization problems can be parameterized with a small number of evaluations (so they still run, but it's much quicker).
3. Tests that involve large data should be adapted in a way that it can be run quickly (e.g., with a subset of the data).

# Starting the DT framework

Follow the instructions in [README.md](./startup/README.md)

# Running Integration Tests

Make sure you can successfully start the DT framework and run the unit tests before attempting to run the integration tests.

The script [run_integration_tests.ps1](./run_integration_tests.ps1) contains the instructions.

# Handling Datasets

1. Small datasets can be committed as csv files into the dataset folder.
2. Each dataset should come in its own folder, with some documentation explaining what it is all about, and a description of the physical setup.
3. Medium sized datasets should be zipped (same name as the csv file it contains, so it's easy to find when tests fail to load it).
4. Large datasets need to be put elsewhere (but a small version of the same dataset should be committed to this repo.)
