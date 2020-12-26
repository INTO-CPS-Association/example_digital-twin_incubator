Start-Process -WorkingDirectory ".\communication\installation" powershell {
    $Host.UI.RawUI.WindowTitle = "'RabbitMQ Server'";
    docker-compose up --build;
    pause
}

Start-Process -WorkingDirectory ".\digital_twin\data_access\influxdbserver\" powershell {
    $Host.UI.RawUI.WindowTitle = "'InfluxDB Server'";
    docker-compose up --build;
    pause
}

echo "Press enter after both rabbitmq server and influxdb starts."

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

Start-Sleep -Seconds 1

Start-Process powershell {
    $Host.UI.RawUI.WindowTitle = "'Influx Data Recorder'";
    python -m mock_physical_twin.start_influx_data_recorder;
    pause
}

