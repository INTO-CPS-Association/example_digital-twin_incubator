import pika
import sys
sys.path.append("../shared")
try:
    from connection_parameters import *
    from protocol import *
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

    # 声明一个queue
    channel.queue_declare(queue='hello')

    # exchange为空的时候，routing_key就是指定的queue值
    channel.basic_publish(exchange='', routing_key='hello', body=bytes('Hello Worlddd!','utf-8'))
    print(" [x] Sent 'Hello World!'")
    # 关闭连接
    connection.close()