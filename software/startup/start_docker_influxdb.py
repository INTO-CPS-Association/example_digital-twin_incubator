import docker_service_starter as ds
import requests
containerName = "influxdb-server"
logFileName = "influxdb.log"
dockerComposeDirectoryPath = "../digital_twin/data_access/influxdbserver"
sleepTimeBetweenAttempts = 1
maxAttempts = 10
def test_connection_function():
    try:
        r = requests.get("http://localhost:8086/health")
        if r.status_code == 200:
            print("InfluxDB ready:\n " + r.text)
            return True
        else:
            print("InfluxDBn ot ready - statuscode: " + str(r.status_code))
    except requests.exceptions.ConnectionError as x:
        print("InfluxDBnot ready - Exception: " + x.__class__.__name__)
    return False

ds.killContainer(containerName)
ds.start(logFileName,
           dockerComposeDirectoryPath,
           test_connection_function, sleepTimeBetweenAttempts, maxAttempts)
ds.killContainer(containerName)