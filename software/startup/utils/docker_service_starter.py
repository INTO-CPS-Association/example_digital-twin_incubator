import docker
import os
import subprocess
import time

defaultDockerComposeCommand = ["docker-compose", "up", "--detach", "--no-build"]


def kill_container(containerName):
    print("Searching for container with the name: " + containerName)
    client = docker.from_env()
    try:
        container = client.containers.get(containerName)
        print("Container status: " + container.status)
        if container.status == "running":
            print("Container is running. Issuing kill request.")
            container.kill()
            print(client.containers.get(containerName).status)
        assert client.containers.get(containerName).status != "running"
    except (docker.errors.NotFound, docker.errors.APIError) as x:
        print("Exception in attempt to kill container: " + str(x))
    finally:
        client.close()


def start(logFilePath, dockerComposeDirectoryPath,
            testConnectionFunction,
            sleepTimeBetweenAttempts,
            maxAttempts):
    print("Log will be stored in: " + os.path.abspath(logFilePath))

    os.makedirs(os.path.dirname(logFilePath), exist_ok=True)

    with open(logFilePath, "wt") as f:
        print("Running docker-compose command: " + " ".join(defaultDockerComposeCommand))
        proc = subprocess.run(defaultDockerComposeCommand, cwd=dockerComposeDirectoryPath, stdout=f)
        if proc.returncode == 0:
            print("docker-compose successful.")
        else:
            print("docker-composed failed:" + str(proc.returncode))
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
                # print("Service is not ready yet. Attempts remaining:" + str(attempts))
                if attempts > 0:
                    time.sleep(sleepTimeBetweenAttempts)
