import sys
import pika
# import json
import os
import csv

# sys.path.append("../../shared/")
# from communication.shared.connection_parameters import *
# from communication.shared.protocol import *

RASPBERRY_IP = "10.17.98.239"
RASPBERRY_PORT = 5672
PIKA_USERNAME = "incubator"
PIKA_PASSWORD = "incubator"
PIKA_EXCHANGE = "Incubator_AMQP"
PIKA_EXCHANGE_TYPE = "topic"
PIKA_VHOST = "/"

ROUTING_KEY_STATE = "incubator.driver.state"
ROUTING_KEY_HEATER = "incubator.hardware.gpio.heater.on"
ROUTING_KEY_FAN = "incubator.hardware.gpio.fan.on"
ENCODING = "ascii"
HEAT_CTRL_QUEUE = "heater_control"
FAN_CTRL_QUEUE = "fan_control"


outfile = "output.csv"
overwrite = True
header_written = False
csv_writer = None
out_file_handle = None
print_exclude = "time"
line_format = "{:20} {:10} {:10} {:10} {:10} {:10} {:10}"

def read_state(ch, method, properties, body):
    global header_written

    body_json = eval(body)

    if not header_written:
        header = list(body_json.keys())
        csv_writer.writerow(header) 
        headers_to_print = [h for h in header if not h.startswith(print_exclude)]
        assert len(headers_to_print)==7
        print(line_format.format(*headers_to_print))
        header_written = True
    
    values = list(body_json.values())
    csv_writer.writerow(values)
    out_file_handle.flush()
    header_to_print = [h for h in body_json.keys() if not h.startswith(print_exclude)]
    values_to_print = [str(body_json[h]) for h in header_to_print]
    print(line_format.format(*values_to_print))


if __name__ == '__main__':
    if os.path.isfile(outfile) and not overwrite:
        print(f"Error: Output file {outfile} already exists. If you wish to overwrite, use that. Exiting...")
        sys.exit(1)

    credentials = pika.PlainCredentials(PIKA_USERNAME, PIKA_PASSWORD)
    parameters = pika.ConnectionParameters(RASPBERRY_IP,
                                           RASPBERRY_PORT,
                                           PIKA_VHOST,
                                           credentials)
    connection = pika.BlockingConnection(parameters)

    channel = connection.channel()
    channel.exchange_declare(exchange=PIKA_EXCHANGE, exchange_type=PIKA_EXCHANGE_TYPE)
    
    queue_name = "monitor"
    channel.queue_declare(queue_name, exclusive=True)
    channel.queue_bind(
            exchange=PIKA_EXCHANGE,
            queue=queue_name,
            routing_key=ROUTING_KEY_STATE
        )
    
    with open(outfile, 'w') as out:
        out_file_handle = out
        csv_writer = csv.writer(out)
        channel.basic_consume(queue=queue_name, on_message_callback=read_state, auto_ack=True)

        try:
            print("Ready to receive.")
            channel.start_consuming()
        except KeyboardInterrupt:
            print("Closing connection.")
            connection.close()