from incubator.config import config_logger, load_config
from digital_twin.monitoring.kalman_filter_plant_server import KalmanFilterPlantServer


def start_plant_kalmanfilter(ok_queue=None):
    config_logger("logging.conf")
    config = load_config("startup.conf")

    monitor = KalmanFilterPlantServer(rabbit_config=config["rabbitmq"])

    monitor.setup(step_size=3.0, std_dev=0.1,
                  **(config["digital_twin"]["models"]["plant"]["param4"]))

    if ok_queue is not None:
        ok_queue.put("OK")

    monitor.start_monitoring()


if __name__ == '__main__':
    start_plant_kalmanfilter()
