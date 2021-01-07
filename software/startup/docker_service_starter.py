import docker
import os
import subprocess
import time

defaultDockerComposeCommand = ["docker-compose", "up", "--detach", "--build"]


def killContainer(containerName):
    print("Searching for container with the name: " + containerName)
    client = docker.from_env()
    try:
        container = client.containers.get(containerName)
        if container.status == "running":
            print("Container is running. Issuing kill request.")
            container.kill()
    except (docker.errors.NotFound, docker.errors.APIError) as x:
        print("Exception in attempt to kill container: " + str(x))


def start(logFilePath, dockerComposeDirectoryPath,
            testConnectionFunction,
            sleepTimeBetweenAttempts,
            maxAttempts):
    with open(logFilePath, "wt") as f:
        print("Running docker-compose command: " + " ".join(defaultDockerComposeCommand))
        print("Log will be stored in: " + os.path.abspath(logFilePath))
        proc = subprocess.run(defaultDockerComposeCommand, cwd=dockerComposeDirectoryPath, stdout=f)
        if proc.returncode == 0:
            print("docker-compose terminated succesfully.")
        else:
            print("docker-composed failed to terminate:" + str(proc.returncode))
            return False
        service_ready = False
        attempts = maxAttempts
        while service_ready is False and attempts > 0:
            r = testConnectionFunction()
            if r is True:
                print("Service is ready");
                service_ready = True
            else:
                attempts -= 1
                print("Service is not ready yet. Attempts remaning:" + str(attempts))
                if attempts > 0:
                    time.sleep(sleepTimeBetweenAttempts)
