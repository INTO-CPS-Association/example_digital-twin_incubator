import docker_service_starter as ds
import requests

if __name__ == '__main__':
    containerName = "rabbitmq-server"
    logFileName = "rabbitmq.log"
    dockerComposeDirectoryPath = "../communication/installation"
    sleepTimeBetweenAttempts = 1
    maxAttempts = 10


    def test_connection_function():
        try:
            r = requests.get("http://localhost:15672/api/overview", auth=('incubator', 'incubator'))
            if r.status_code == 200:
                print("RabbitMQ ready:\n " + r.text)
                return True
        except requests.exceptions.ConnectionError as x:
            print("RabbitMQ not ready - Exception: " + x.__class__.__name__)
        return False


    ds.killContainer(containerName)
    ds.start(logFileName,
             dockerComposeDirectoryPath,
             test_connection_function, sleepTimeBetweenAttempts, maxAttempts)
    ds.killContainer(containerName)

# import subprocess
# import docker
# import requests
# import time
# import os
# from docker_service_starter import *
# dockerRelativeLocation = "../communication/installation"
# command = ["docker-compose", "up", "--detach", "--build"]
# containerName = "rabbitmq-server"
# sleepBetweenConnectionAttempts = 1
# maxConnectionAttempts = 10
# logFileName = "rabbitmq.log"
#
#
# def testConnection():
#     return
#
#
# def killContainer(containerName):
#     print("Searching for container with the name: " + containerName)
#     client = docker.from_env()
#     try:
#         container = client.containers.get(containerName)
#         if container.status == "running":
#             print("Container is running. Issuing kill request.")
#             container.kill()
#     except (docker.errors.NotFound, docker.errors.APIError) as x:
#         print("Exception in attempt to kill container: " + str(x))
#
#
# if __name__ == '__main__':
#     killContainer(containerName)
#
#     f = open(logFileName, "wt")
#     print("Running docker-compose command: " + " ".join(command))
#     print("Log will be stored in: " +os.path.abspath(logFileName))
#     proc = subprocess.run(command, cwd=dockerRelativeLocation, stdout=f)
#     if proc.returncode == 0:
#         print("docker-compose terminated succesfully.")
#     else:
#         print("docker-composed failed to terminate:" + str(proc.returncode))
#
#     rabbitmq_ready = False
#     attempts = maxConnectionAttempts
#     while rabbitmq_ready is False and attempts > 0:
#         try:
#             r = testConnection()
#             if r.status_code == 200:
#                 print("RabbitMQ ready:\n " + r.text)
#                 rabbitmq_ready = True
#         except requests.exceptions.ConnectionError as x:
#             print("RabbitMQ not ready - Exception: " + x.__class__.__name__)
#             time.sleep(sleepBetweenConnectionAttempts)
#             attempts -= 1
#
#     f.flush()
#     f.close()
#     killContainer(containerName)
