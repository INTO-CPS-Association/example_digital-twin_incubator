import pika
import sys
sys.path.append("../shared")
try:
    from connection_parameters import *
    from protocol import *
except:
    raise


def callback(ch, method, properties, body):
    print(" [x] Received %r" % (body,))


if __name__ == '__main__':
    credentials = pika.PlainCredentials(PIKA_USERNAME, PIKA_PASSWORD)
    parameters = pika.ConnectionParameters(RASPBERRY_IP,
                                           RASPBERRY_PORT,
                                           PIKA_VHOST,
                                           credentials)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    # 声明queue
    channel.queue_declare(queue='hello')

    print(' [*] Waiting for messages. To exit press CTRL+C')

    # 收到指定消息的回调设置
    channel.basic_consume(queue="hello", on_message_callback=callback,auto_ack=True)
    # channel.basic_consume(callback, queue="hello",  no_ack=True,)
    # 开始循环监听
    channel.start_consuming()