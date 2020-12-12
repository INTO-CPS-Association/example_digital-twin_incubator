This folder contains the code that makes the digital twin possible.

# Directory Structure

```
├───communication -- Contains code to establish the communication layer between physical twin and digital twin.
├───digital_twin -- Code that forms the digital twin.
├───old_software -- Old code that is still being organized
├───physical_twin -- Code that implements the physical twin
└───tests -- Tests that exercise the code above.
```

# Running the Tests

1. Open terminal in this folder.
2. Optional: create a virtual environment: `python -m venv venv`
3. Optional: activate the virtual environment (there are multiple possible activate scripts. Pick the one for you command line interface.): 
   1. Windows Powershell:`.\venv\Scripts\Activate.ps1` 
   2. Linux/Mac: `source venv/bin/activate`
4. Install dependencies (incomplete list):
   1. `pip install OOModellingPython`
5. Use Unittest to run the tests.
   1. Example: `python -m unittest discover tests -p '*.py'`

# Creating Tests

Each test should correspond to one experiment, and each experiment should be targeted at answering one question.

Commit the tests in a way that they can be run automatically and quickly:

1. Comment out the `plt.show()` so that no plot windows are shown to the user (these block the execution of python).
2. Optimization problems can be parameterized with a small number of evaluations (so they still run, but it's much quicker).
3. Tests that involve large data should be parameterized in a way that it can be run quickly (e.g., with a subset of the data).

# Handling Datasets

1. Small datasets can be committed as csv files into the dataset folder.
2. Each dataset should come in its own folder, with some documentation explaining what it is all about, and a description of the physical setup.
3. Medium sized datasets should be zipped (same name as the csv file it contains, so it's easy to find when tests fail to load it).
4. Large datasets need to be put elsewhere (but a small version of the same dataset should be committed to this repo.)
