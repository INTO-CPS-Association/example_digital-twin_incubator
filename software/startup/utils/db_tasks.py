import os
import shutil
import zipfile


def setup_db(influxdb_docker_dir="../../digital_twin/data_access/influxdbserver"):
    db_folder = os.path.join(influxdb_docker_dir, "influxdb")
    shutil.rmtree(os.path.join(influxdb_docker_dir, "influxdb"), ignore_errors=True)
    os.mkdir(db_folder)
    with zipfile.ZipFile(os.path.join(influxdb_docker_dir, "influxdb.zip"), 'r') as zip_ref:
        zip_ref.extractall(db_folder)


if __name__ == '__main__':
    setup_db()
