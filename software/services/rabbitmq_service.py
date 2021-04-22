from testcontainer_python_rabbitmq import RabbitMQContainer

class rabbitmq_service(RabbitMQContainer):

    def get_rabbitmq_conf(self):
        import socket

        return '''rabbitmq: {
        ip = 127.0.0.1
        port = ''' + str(self.get_amqp_port()) + '''
        username = guest
        password = guest
        exchange = Incubator_AMQP
        type = topic
        vhost = /
    }'''