import pika
import json
try:
    from communication.shared.connection_parameters import *
    from communication.shared.protocol import *
except:
    raise


def callback(ch, method, properties, body):
    body_json = json.loads(body)
    print(" [x] Received %r" % (body,))
    print(body_json['time'])


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
    # channel.basic_consume(queue="hello", on_message_callback=callback,auto_ack=True)
    # channel.basic_consume(callback, queue="hello",  no_ack=True,)
    # 开始循环监听
    (method, properties, body) = channel.basic_get(queue="hello",auto_ack=True)
    if body is not None:
        body_json = json.loads(body)
    print(" [x] Received %r" % (body))
    # channel.start_consuming()