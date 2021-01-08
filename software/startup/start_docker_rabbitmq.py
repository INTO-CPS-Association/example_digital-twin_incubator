import requests

from startup.utils.docker_service_starter import kill_container, start


def start_docker_rabbitmq():
    containerName = "rabbitmq-server"
    logFileName = "logs/rabbitmq.log"
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
            # print("RabbitMQ not ready - Exception: " + x.__class__.__name__)
            pass
        return False

    kill_container(containerName)
    start(logFileName,
             dockerComposeDirectoryPath,
             test_connection_function, sleepTimeBetweenAttempts, maxAttempts)


if __name__ == '__main__':
    start_docker_rabbitmq()
