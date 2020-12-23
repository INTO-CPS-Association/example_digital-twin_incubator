Code for mocking up an incubator using a local rabbitmq server instance.

The mock incubator contains the following components:
- An incubator plan model (`FourParameterIncubatorPlant` class)
- The `IncubatorDriver`
- The `ControllerPhysical`

Here the `FourParameterIncubatorPlant` replaces the physical incubator, and the `IncubatorDriver` will read values and actuate on the `FourParameterIncubatorPlant`.

How to start a mock incubator:
1. Start the rabbitmq server. Follow the instructions in [README.md](../communication/installation/README.md).
2. Start each of the components in the following order, on different terminals, and with the appropriate virtual environment:
    1. Run [start_incubator_plant_simulation.py](./start_incubator_plant_simulation.py)
    2. Run [start_low_level_driver_mockup.py](./start_low_level_driver_mockup.py).
    3. Run [start_controller_physical.py](./start_controller_physical.py).