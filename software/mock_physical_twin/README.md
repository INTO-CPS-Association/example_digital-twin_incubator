Code for mocking up an incubator using a local rabbitmq server instance.

The mock incubator contains the following components:
- An incubator plan model (`FourParameterIncubatorPlant` class)
- The `IncubatorDriver`
- The `ControllerPhysical`

Here the `FourParameterIncubatorPlant` replaces the physical incubator, and the `IncubatorDriver` will read values and actuate on the `FourParameterIncubatorPlant`.

How to start a mock incubator: [start_mock_physical_twin.ps1](../scripts/start_mock_physical_twin.ps1)
