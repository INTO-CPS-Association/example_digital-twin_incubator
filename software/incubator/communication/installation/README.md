To start the rabbitmq server, run:
``` Powershell
# start rabbitmq
PS software\incubator\communication\installation> docker-compose up --detach --build
[MACOS: docker compose up --detach --build]

# Check logs of rabbitmq-server
PS software\incubator\communication\installation> docker logs rabbitmq-server

# Run script to test server (assumes you have correct environment)
cd [RepoRoot]\software\
[Activate virtual environment]
PS software> python -m incubator.communication.installation.test_server

# Stop and remove the server
PS software> docker-compose down -v
[MACOS: docker compose down -v]
```

The script should produce:
```
Sending message...
Message sent.
Retrieving message. Received message is {'text': '321'}
```

More information about the [Dockerfile](./Dockerfile):
https://hub.docker.com/_/rabbitmq

Management of local rabbitmq:
1. Start rabbitmq server
2. Open http://localhost:15672/ on your browser.
3. User and pass are in the [Dockerfile](./Dockerfile)
