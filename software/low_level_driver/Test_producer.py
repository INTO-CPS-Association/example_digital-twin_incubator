import pika
import sys
import json

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
#print("passing connection phase")
channel.exchange_declare(exchange='Incubator_AMQP', exchange_type='topic')

routing_key = "incubator.hardware.gpio.fanManipulate"#sys.argv[1] if len(sys.argv) > 2 else 'anonymous.info'
message = {
     "Time": True,
     "readTemperature2": False,
}#' '.join(sys.argv[2:]) or 'Hello World!'
channel.basic_publish(
    exchange='Incubator_AMQP', routing_key=routing_key, body=json.dumps(message))
print(" [x] Sent %r:%r" % (routing_key, message))
connection.close()