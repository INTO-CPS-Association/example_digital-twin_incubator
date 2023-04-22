# First time configuration of influxdb server

Run the following if this is the first time you're starting the influxdb server:
1. Unzip [influxdb.zip](./influxdb.zip) into a new directory called [influxdb](./influxdb).
   The directory tree should look like: 
   ```powershell
   influxdb
   │   config.yaml
   │   docker-compose.yml
   │   Dockerfile
   │   influxdb.zip
   │   README.md
   │   test_server.py
   └── influxdb
       │   influxd.bolt
       └── engine
           │   data
           └── wal
   ```
2. This directory tree will contain all the data stored in influxdb, even if the virtual machine is deleted. So you can back it up if you want to protect the data.
3. [Start the influxdb server](#start-influxdb-server).

# Start influxdb server

To start the influxdb server, run:
1. Start influxdb:
   ```Powershell
   PS software\digital_twin\data_access\influxdbserver> docker-compose up --detach --build
   ```
2. Run script to test db connection
   ```Powershell
   PS software\digital_twin\data_access\influxdbserver> cd [RepoRoot]\software
   [Activate virtual environment]
   PS software> python -m digital_twin.data_access.influxdbserver.test_server
   ```
3. See the data produced by the script by logging in to http://localhost:8086/ (user and password below) and opening the test dashboard.
4. Stop and remove the server:
   ```Powershell
   docker-compose down -v
   ```

More information: https://docs.influxdata.com/influxdb/v2.0/get-started/

# Management of Influxdb

1. Start influxdb server
2. Open http://localhost:8086/ on your browser.
3. Alternative, open a terminal in the container: `docker exec -it influxdb-server /bin/bash`

# Initial Setup of Database

This has been done once, and there's no need to repeat it.
But it is left here in case we lose the file [influxdb.zip](./influxdb.zip).

1. Open http://localhost:8086/
2. Press Get-Started
3. Enter information:
    ```
    user: incubator
    pass: incubator
    organization: incubator
    bucket: incubator 
    ```
4. Run the [test_server.py](./test_server.py) script to start pushing random data onto the db.
5. Create dashboards by importing the json files in [dashboards](./dashboards) in the management page http://localhost:8086/

# Common Errors
