To start the rabbitmq server, run:
```
# start rabbitmq
docker-compose up --detach --build

# Check logs of rabbitmq-server
docker logs rabbitmq-server

# Run script to test server (assumes you have correct environment)
cd [RepoRoot]\software
[Activate virtual environment]
python -m communication.installation.test_server

# Stop and remove the server
docker-compose down -v
```

More information in:
https://hub.docker.com/_/rabbitmq

Management of rabbitmq:
1. Start rabbitmq server
2. Open http://localhost:15672/ on your browser.
3. User and pass are in the Dockerfile


To install the Docker:
1. Download the installer from https://docs.docker.com/docker-for-windows/install/
2. Before installation, open a PowerShell console as Administrator and run the following command (Reference: https://docs.microsoft.com/en-us/virtualization/hyper-v-on-windows/quick-start/enable-hyper-v):
```
Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V -All
```
3. Install the Docker with the Installer. 
Tip: I installed a WSL on my computer which failed the Docker after the installation. So during the installation, I unchecked the WSL relative stuff before finishing the Dock installation. 