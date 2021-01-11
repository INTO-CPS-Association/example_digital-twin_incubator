from startup.start_docker_influxdb import stop_docker_influxdb
from startup.start_docker_rabbitmq import stop_docker_rabbitmq

if __name__ == '__main__':
    stop_docker_rabbitmq()
    stop_docker_influxdb()
