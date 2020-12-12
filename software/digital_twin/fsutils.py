import os
import sys


def resource_file_path(filename):
    """ Search for filename in the list of directories specified in the
        PYTHONPATH environment variable.
        Taken from https://stackoverflow.com/questions/45806838/can-i-locate-resource-file-in-pythonpath
    """
    pythonpath = os.environ.get("PYTHONPATH")
    if pythonpath is None:
        directories = ['.']
    else:
        directories = pythonpath.split(os.pathsep)
    for d in directories:
        filepath = os.path.join(d, filename)
        if os.path.exists(filepath):
            return filepath

    print(f"File not found: {filename}")
    print(f"Tried the following directories:")
    print(directories)
    sys.exit(1)


def get_all_files_with_extension(directory, extension):
    files = []
    for file in os.listdir(directory):
        if file.endswith(extension):
            files.append(os.path.join(directory, file))
    return files