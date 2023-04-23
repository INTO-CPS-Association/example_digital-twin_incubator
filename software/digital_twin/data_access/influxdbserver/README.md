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

## Unauthorized API access

If while running `test_server` in [Start influxdb server](#start-influxdb-server), you get an error resembling the following:
```
> write_api.write(bucket, org, point)
(Pdb) config["influxdb"]
ConfigTree([('url', 'http://localhost:8086'), ('token', '-g7q1xIvZqY8BA82zC7uMmJS1zeTj61SQjDCY40DkY6IpPBpvna2YoQPdSeENiekgVLMd91xA95smSkhhbtO7Q=='), ('org', 'incubator'), ('bucket', 'incubator')])
influxdb_client.rest.ApiException: (401)
Reason: Unauthorized
HTTP response headers: HTTPHeaderDict({'Content-Type': 'application/json; charset=utf-8', 'X-Platform-Error-Code': 'unauthorized', 'Date': 'Wed, 31 Aug 2022 09:35:17 GMT', 'Content-Length': '55'})
HTTP response body: {"code":"unauthorized","message":"unauthorized access"}
-> write_api.write(bucket, org, point)
```

Then the cause is the token used in the [startup.conf](../../../startup.conf) needs to be updated.
To fix open the InfluxDB web management page, go to InfluxDB->Tokens and generate a new token. Then update [startup.conf](../../../startup.conf) with the new token.

Original issue described in [#23](https://github.com/INTO-CPS-Association/example_digital-twin_incubator/issues/23).
