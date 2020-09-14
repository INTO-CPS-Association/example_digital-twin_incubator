import pika
import sys

IP_raspberry = '10.17.98.141'
IP_myLaptop =  '10.17.98.164'

credentials = pika.PlainCredentials('incubator', 'incubator')
parameters = pika.ConnectionParameters('10.17.98.141',
                                   5672,
                                   '/',
                                   credentials)

connection = pika.BlockingConnection(parameters)


# connection = pika.BlockingConnection(
#     pika.ConnectionParameters(host='10.192.17.148',port=5672))
channel = connection.channel()
print("passing connection phase")
channel.exchange_declare(exchange='topic_logs', exchange_type='topic')

routing_key = sys.argv[1] if len(sys.argv) > 2 else 'anonymous.info'
message = ' '.join(sys.argv[2:]) or 'Hello World!'
channel.basic_publish(
    exchange='topic_logs', routing_key=routing_key, body=message)
print(" [x] Sent %r:%r" % (routing_key, message))
connection.close()