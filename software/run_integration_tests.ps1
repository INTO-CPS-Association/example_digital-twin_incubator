# Set environment variable CLIMODE, so that tests know that they should not plot stuff.
$Env:CLIMODE = "ON"

# Run unittest in discovery mode for the integration_tests folder
& python -m unittest discover --failfast -v integration_tests -p "*.py"
