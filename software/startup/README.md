This is where the code that start the DT services is located.

Each service runs in its own process and has as a corresponding start script.

Before starting any service, make sure you have [docker](https://www.docker.com/products/docker-desktop) installed (see below), and that you have followed the instructions in:
1. [Rabbitmq README](../incubator/communication/installation/README.md)
2. [Influxdb README](../digital_twin/data_access/influxdbserver/README.md)

The script [start_all_services.py](./start_all_services.py) starts all services (including the mock of the incubator hardware). The library module can be run as a script by giving -m to the python command as follows:

```bash
software$ python -m startup.start_all_services
```

The service that mimics the real-time incubator is in [start_incubator_realtime_mockup.py](./start_incubator_realtime_mockup.py)

After starting the influxdb service, you can login to http://[Influxdb_IP]:8086/ to see the influxdb management page, 
were you can create dashboards to see the data produced by the incubator.

After starting all services successfully, the controller service will start producing output that looks like the following:
````
time           execution_interval  elapsed  heater_on  fan_on  t1     box_air_temperature  state 
19/11 16:17:59  3.00                0.01     True       False   10.70  19.68                Heating
19/11 16:18:02  3.00                0.03     True       True    10.70  19.57                Heating
19/11 16:18:05  3.00                0.01     True       True    10.70  19.57                Heating
19/11 16:18:08  3.00                0.01     True       True    10.69  19.47                Heating
19/11 16:18:11  3.00                0.01     True       True    10.69  19.41                Heating
````

## To install Docker

1. Download the installer from https://docs.docker.com/docker-for-windows/install/
2. Before installation, open a PowerShell console as Administrator and run the following command (Reference: https://docs.microsoft.com/en-us/virtualization/hyper-v-on-windows/quick-start/enable-hyper-v):
```
Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V -All
```
3. Install the Docker with the Installer. 
Tip: I installed a WSL on my computer which failed the Docker after the installation. So during the installation, I unchecked the WSL relative stuff before finishing the Dock installation. 