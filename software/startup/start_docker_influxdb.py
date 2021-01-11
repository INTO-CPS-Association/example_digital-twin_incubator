from digital_twin.fsutils import resource_file_path
from startup.utils import docker_service_starter as ds
import requests

from startup.utils.docker_service_starter import kill_container

containerName = "influxdb-server"


def start_docker_influxdb():
    logFileName = "logs/influxdb.log"
    dockerComposeDirectoryPath = resource_file_path("digital_twin/data_access/influxdbserver")
    sleepTimeBetweenAttempts = 1
    maxAttempts = 10

    def test_connection_function():
        try:
            r = requests.get("http://localhost:8086/health")
            if r.status_code == 200:
                print("InfluxDB ready:\n " + r.text)
                return True
            else:
                pass
                # print("InfluxDBn not ready - statuscode: " + str(r.status_code))
        except requests.exceptions.ConnectionError as x:
            # print("InfluxDBnot ready - Exception: " + x.__class__.__name__)
            pass
        return False

    ds.kill_container(containerName)
    ds.start(logFileName,
             dockerComposeDirectoryPath,
             test_connection_function, sleepTimeBetweenAttempts, maxAttempts)


def stop_docker_influxdb():
    kill_container(containerName)


if __name__ == '__main__':
    start_docker_influxdb()
