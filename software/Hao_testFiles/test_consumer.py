import pika
import sys
IP_raspberry = '10.17.98.141'
IP_myLaptop =  '10.17.98.164'
credentials = pika.PlainCredentials('incubator', 'incubator')
parameters = pika.ConnectionParameters(IP_raspberry,
                                   5672,
                                   '/',
                                   credentials)

connection = pika.BlockingConnection(parameters)

# connection = pika.BlockingConnection(
#     pika.ConnectionParameters(host='10.192.17.148',port=15672))
channel = connection.channel()

channel.exchange_declare(exchange='topic_logs', exchange_type='topic')

result = channel.queue_declare('', exclusive=True)
queue_name = result.method.queue

binding_keys = sys.argv[1:]
if not binding_keys:
    sys.stderr.write("Usage: %s [binding_key]...\n" % sys.argv[0])
    sys.exit(1)

for binding_key in binding_keys:
    channel.queue_bind(
        exchange='topic_logs', queue=queue_name, routing_key=binding_key)

print(' [*] Waiting for logs. To exit press CTRL+C')


def callback(ch, method, properties, body):
    print(" [x] %r:%r" % (method.routing_key, body))


channel.basic_consume(
    queue=queue_name, on_message_callback=callback, auto_ack=True)

channel.start_consuming()