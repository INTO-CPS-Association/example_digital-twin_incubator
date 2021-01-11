import logging.config
import os
from pyhocon import ConfigFactory


def resource_file_path(filename):
    """ Search for filename in the list of directories specified in the
        PYTHONPATH environment variable.
        Taken from https://stackoverflow.com/questions/45806838/can-i-locate-resource-file-in-pythonpath
    """
    pythonpath = os.environ.get("PYTHONPATH")
    if pythonpath is None:
        directories = ['.']
    else:
        directories = pythonpath.split(os.pathsep) + ['.']

    for d in directories:
        filepath = os.path.join(d, filename)
        if os.path.exists(filepath):
            return filepath

    print(f"File not found: {filename}")
    print(f"Tried the following directories:")
    print(directories)
    raise ValueError("File not found: {filename}")


def load_config(config_file_name):
    file_path = resource_file_path(config_file_name)
    config = ConfigFactory.parse_file(file_path)
    return config


def config_logger(logger_conf_file):
    logging.config.fileConfig(resource_file_path(logger_conf_file))