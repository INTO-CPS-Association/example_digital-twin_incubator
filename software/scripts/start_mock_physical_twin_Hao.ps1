Start-Process -WorkingDirectory ".\communication\installation" powershell {
    $Host.UI.RawUI.WindowTitle = "'RabbitMQ Server'";
    conda activate Incubator;
    docker-compose up --build
}

Echo "Press enter after rabbitmq server starts."
Pause

Start-Process powershell {
    $Host.UI.RawUI.WindowTitle = "'Plant Simulator'";
    conda activate Incubator;
    python -m mock_physical_twin.start_incubator_plant_simulation
}

Start-Process powershell {
    $Host.UI.RawUI.WindowTitle = "'Low Level Driver'";
    conda activate Incubator;
    python -m mock_physical_twin.start_low_level_driver_mockup
}

Start-Process powershell {
    $Host.UI.RawUI.WindowTitle = "'Controller Physical'";
    conda activate Incubator;
    python -m mock_physical_twin.start_controller_physical
}
