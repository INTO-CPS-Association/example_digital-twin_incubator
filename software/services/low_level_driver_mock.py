import tempfile
from startup import start_low_level_driver_mockupv2
from startup.utils.start_as_daemon import start_as_daemon_with_args


class low_level_driver_mock:
    def __init__(self, rabbitmq_service, log_configuration: str):
        self.rabbitmq_service = rabbitmq_service
        self.log_configuration = log_configuration
        self.processes = []
        self.tempfile = None

    def __enter__(self):
        # Get the rabbitmq configuration
        rabbitmqConfiguration = self.rabbitmq_service.get_rabbitmq_conf()
        self.tempfile = tempfile.NamedTemporaryFile(delete=False)
        self.tempfile.write(bytes(rabbitmqConfiguration, 'utf-8'))
        self.tempfile.flush()
        args = {"configuration": self.tempfile.name, "logging_configuration": str(self.log_configuration)}

        self.processes.append(start_as_daemon_with_args(start_low_level_driver_mockupv2.start_low_level_driver_mockupv2, args))

    def __exit__(self, type, value, traceback):
        for p in self.processes:
            print(f"Killing {p.name}... ")
            p.kill()
            print("OK")
        if self.tempfile is not None:
            self.tempfile.close()
