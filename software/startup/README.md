Code for mocking up an incubator using a local rabbitmq server instance.

Here the `FourParameterIncubatorPlant` replaces the physical incubator, and the `IncubatorDriver` will read values and actuate on the `FourParameterIncubatorPlant`.

How to start a mock incubator: [start_mock_physical_twin.ps1](../scripts/start_mock_physical_twin.ps1)

After starting the incubator, you can login to http://<Influxdb IP>:8086/ to see the influxdb management page, 
were you can create dashboards to see the data produced by the incubator.
