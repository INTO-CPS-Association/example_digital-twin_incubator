FROM quay.io/influxdb/influxdb:v2.0.3

COPY ./config.yaml /etc/influxdb/config.yaml

RUN ["/entrypoint.sh"]

ENV INFLUXD_CONFIG_PATH /etc/influxdb/

CMD ["influxd"]
