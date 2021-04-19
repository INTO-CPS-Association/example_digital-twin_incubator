from abc import abstractmethod

import paramiko
import scp
import threading
from pathlib import Path
import socket
from contextlib import contextmanager, closing


class Experiment:

    @abstractmethod
    def describe(self):
        """Provide a short description of the experiment. What knowledge is gained?"""
        pass

    def configure(self):
        """Generate any configuration required for the experiment"""
        pass

    def cleanup(self):
        """Remove any intermediate resources using during the execution"""
        pass

    def run(self):
        """Primary run of the experiment"""
        self.configure()
        self.do_experiment()
        self.post_process()
        report = self.generate_report()
        self.cleanup()
        return report

    @abstractmethod
    def do_experiment(self):
        """This is the implementation of the experiment"""
        pass

    def post_process(self):
        """Process any results generated by executing the experiment"""
        pass

    def generate_report(self) -> Path:
        """Generate a report from the experiment. Must return a path to the report root"""
        pass

    def get_working_dir(self) -> Path:
        """Get a working director for this experiment"""
        path = Path("work") / type(self).__name__
        if not path.exists():
            path.mkdir(parents=True)
        return path


class ExperimentWithServices(Experiment):

    def get_service_host_hostname(self):
        import socket
        return socket.gethostbyname(socket.gethostname())

    @abstractmethod
    def get_services(self):
        return []

    def run(self):
        """Primary run of the experiment"""

        services = self.get_services()
        try:
            for s in services:
                s.__enter__()
            self.configure()
            self.do_experiment()
        finally:
            for s in services:
                s.__exit__(None, None, None)
        self.post_process()
        report = self.generate_report()
        self.cleanup()
        return report


class OnTargetExperiment(ExperimentWithServices):

    @abstractmethod
    def configure_target(self):
        """Generate all configuration needed on the target"""
        pass

    @abstractmethod
    def configure_local(self):
        """Generate all configuration needed on the locally"""
        pass

    def configure(self):
        self.configure_target()
        self.configure_local()

    def do_experiment(self):
        self.setup_target()
        target_thread = threading.Thread(target=self.do_target_experiment,
                                         daemon=True)
        target_thread.start()
        self.do_local_experiment()
        target_thread.join(timeout=60)
        self.teardown_target()

    @abstractmethod
    def setup_target(self):
        """Prepare the target. i.e. upload any needed program files to the target"""
        pass

    @abstractmethod
    def teardown_target(self):
        """Remove any resources from the target used for the experiment"""
        pass

    @abstractmethod
    def do_local_experiment(self):
        """Execute the local experiment. Local experiments are meant to be the prime driver of the experiment"""
        pass

    @abstractmethod
    def do_target_experiment(self):
        """Execute the target experiment. i.e. run the uploaded application on target"""
        pass

# class ProfilingExperiment(Experiment):
#     def configure(self):
#         pass
#
#     def start_services(self):
#         pass
#
#     def start_target_application(self):
#         pass
#
#     def start_local_experiment(self):
#         pass
#
#     def stop_services(self):
#         pass
#
#     def post_process(self):
#         pass
#
#     def generate_report(self):
#         pass
#
#     def run(self):
#         self.configure()
#         self.start_services()
#         self.start_target_application()
#         self.start_local_experiment()
#         self.stop_services()
#         self.post_process()
#         self.generate_report()
