# Set environment variable CLIMODE, so that tests know that they should not plot stuff.
$Env:CLIMODE = "ON"

# Add the incubator folder to the PYTHONPATH, so that the code within the submodule incubator continues to work without modification.
$Env:PYTHONPATH = "incubator"

# Run unittest in discovery mode for the integration_tests folder
& python -m unittest discover --failfast -v integration_tests -p "*.py"
