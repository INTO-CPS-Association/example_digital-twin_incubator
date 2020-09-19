
# Activate virtual environment
& .\venv\Scripts\Activate.ps1

Push-Location test
$Env:PYTHONPATH="../src"
& python -m unittest discover -p "*.py"
Pop-Location

pause