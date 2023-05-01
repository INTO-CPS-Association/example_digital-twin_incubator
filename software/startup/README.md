# Incubator DT Startup

To start running the incubator DT on the local machine, just make sure you have [docker](https://www.docker.com/products/docker-desktop) installed (see [below](#to-install-docker)), and run
```bash
software$ python -m startup.start_all_services
```
The script [start_all_services.py](./start_all_services.py) starts all DT services, one in its own process. 
the communication is enabled by a docker container running a RabbitMQ server, and the data is recorded in a docker container running InfluxDB.
The service that mimics the real-time incubator is in [start_incubator_realtime_mockup.py](./start_incubator_realtime_mockup.py). This emulates the physical incubator for the convenience of running the DT in a laptop.

After starting all services successfully, the controller service will start producing output that looks like the following:
````
time           execution_interval  elapsed  heater_on  fan_on   room   box_air_temperature  state 
19/11 16:17:59  3.00                0.01     True       False   10.70  19.68                Heating
19/11 16:18:02  3.00                0.03     True       True    10.70  19.57                Heating
19/11 16:18:05  3.00                0.01     True       True    10.70  19.57                Heating
19/11 16:18:08  3.00                0.01     True       True    10.69  19.47                Heating
19/11 16:18:11  3.00                0.01     True       True    10.69  19.41                Heating
````

After starting all services, you can login to http://localhost:8086/ (or more generally http://[Influxdb_IP]:8086/) to see the influxdb management page, were you can create dashboards to see the data produced by the incubator.


## Diagnosing Startup Errors

If any errors show up, check that the RabbitMQ server and InfluxDB are being correctly started. 
Follow the instructions to test them.
1. [Rabbitmq README](../incubator/communication/installation/README.md)
2. [Influxdb README](../digital_twin/data_access/influxdbserver/README.md)

## To install Docker

See [Docker Homepage](https://docs.docker.com/desktop/)
