This is where the code that start the DT services is located.

Each service run in its own process and has as a corresponding start script.

Before starting any service, make sure you have docker installed, and that you have followed the instructions in:
1. [Rabbitmq README](../incubator/communication/installation/README.md)
2. [Influxdb README](../digital_twin/data_access/influxdbserver/README.md)

The script [start_all_services.py](./start_all_services.py) starts all services (including the mock of the incubator hardware). The library module can be run as a script by giving -m to the python command as follows:

```bash
software$ python -m startup.start_all_services
```

The service that mimics the real-time incubator is in [start_incubator_realtime_mockup.py](./start_incubator_realtime_mockup.py)

After starting the influxdb service, you can login to http://<Influxdb IP>:8086/ to see the influxdb management page, 
were you can create dashboards to see the data produced by the incubator.
