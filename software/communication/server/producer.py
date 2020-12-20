import pika
import time
import json
try:
    from communication.shared.connection_parameters import *
    from communication.shared.protocol import *
except:
    raise
if __name__ == '__main__':
    # 创建一个connection
    credentials = pika.PlainCredentials(PIKA_USERNAME, PIKA_PASSWORD)
    parameters = pika.ConnectionParameters(RASPBERRY_IP,
                                           RASPBERRY_PORT,
                                           PIKA_VHOST,
                                           credentials)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    channel.exchange_declare(exchange=PIKA_EXCHANGE, exchange_type=PIKA_EXCHANGE_TYPE)

    # 声明一个queue
    channel.queue_declare(queue='state')
    channel.queue_bind(
        exchange=PIKA_EXCHANGE,
        queue='state',
        routing_key=ROUTING_KEY_STATE
    )

    start = time.time()
    n_sensors = 3
    readings = [] * n_sensors
    timestamps = [] * n_sensors
    for i in range(n_sensors):
        readings.append(34)
        timestamps.append(time.time())
    message = {
        "time": time.time(),
        "execution_interval": 3,
        "heater_on": True,
        "fan_on": False
    }
    for i in range(n_sensors):
        message[f"t{i + 1}"] = readings[i]
        message[f"time_t{i + 1}"] = timestamps[i]
    message["elapsed"] = time.time() - start

    # exchange为空的时候，routing_key就是指定的queue值
    channel.basic_publish(exchange=PIKA_EXCHANGE, routing_key=ROUTING_KEY_STATE, body=json.dumps(message))
    print(f" [x] Sent '{message}'")
    # 关闭连接
    connection.close()
