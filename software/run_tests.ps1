# Set environment variable CLIMODE, so that tests know that they should not plot stuff.
$Env:CLIMODE = "ON"

# Add the incubator folder to the PYTHONPATH, so that the code within the incubator folder continues to work without modification.
$Env:PYTHONPATH = "incubator"

# Run unittest in discovery mode for the tests folder
& python -m unittest discover -v incubator/tests -p "*.py"
