To start the rabbitmq server, run:
```
# start rabbitmq
docker-compose up --detach --build

# Check logs of rabbitmq-server
docker logs rabbitmq-server

# Start the publish.py script
python3 publish.py

# Stop and remove the server
docker-compose down -v
```



More information in:
https://hub.docker.com/_/rabbitmq
