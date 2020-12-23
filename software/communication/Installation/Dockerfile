FROM rabbitmq:3.8.2-management

ENV RABBITMQ_DEFAULT_USER incubator
ENV RABBITMQ_DEFAULT_PASS incubator

RUN rabbitmq-plugins enable --offline rabbitmq_mqtt rabbitmq_federation_management rabbitmq_stomp
