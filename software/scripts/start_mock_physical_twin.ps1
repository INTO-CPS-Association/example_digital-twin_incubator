& .\venv\scripts\Activate.ps1

Start-Process -WorkingDirectory ".\communication\installation" powershell {
    $Host.UI.RawUI.WindowTitle = "'RabbitMQ Server'";
    docker-compose up --build;
    pause
}

Echo "Press enter after rabbitmq server starts."
Pause

Start-Process powershell {
    $Host.UI.RawUI.WindowTitle = "'Plant Simulator'";
    python -m mock_physical_twin.start_incubator_plant_simulation;
    pause
}

Start-Sleep -Seconds 1

Start-Process powershell {
    $Host.UI.RawUI.WindowTitle = "'Low Level Driver'";
    python -m mock_physical_twin.start_low_level_driver_mockup;
    pause
}

Start-Sleep -Seconds 1

Start-Process powershell {
    $Host.UI.RawUI.WindowTitle = "'Controller Physical'";
    python -m mock_physical_twin.start_controller_physical;
    pause
}

