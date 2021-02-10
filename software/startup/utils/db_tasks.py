import os
import shutil
import zipfile

from incubator.config.config import resource_file_path


def setup_db(influxdb_docker_dir="../../digital_twin/data_access/influxdbserver"):
    influx_db_folder_path = resource_file_path(influxdb_docker_dir)
    db_folder = os.path.join(influx_db_folder_path, "influxdb")
    shutil.rmtree(os.path.join(influx_db_folder_path, "influxdb"), ignore_errors=True)
    os.mkdir(db_folder)
    with zipfile.ZipFile(os.path.join(influx_db_folder_path, "influxdb.zip"), 'r') as zip_ref:
        zip_ref.extractall(db_folder)


if __name__ == '__main__':
    setup_db()
