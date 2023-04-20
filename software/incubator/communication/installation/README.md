To start the rabbitmq server, run from the directory where this readme file is:
```
# start rabbitmq
docker-compose up --detach --build
[MACOS: docker compose up --detach --build]

# Check logs of rabbitmq-server
docker logs rabbitmq-server

# Run script to test server (assumes you have correct environment)
cd [RepoRoot]\software\
[Activate virtual environment]
cd incubator
python -m communication.installation.test_server

# Stop and remove the server
docker-compose down -v
[MACOS: docker compose down -v]
```

More information about the [Dockerfile](./Dockerfile):
https://hub.docker.com/_/rabbitmq

Management of rabbitmq:
1. Start rabbitmq server
2. Open http://localhost:15672/ on your browser.
3. User and pass are in the [Dockerfile](./Dockerfile)
