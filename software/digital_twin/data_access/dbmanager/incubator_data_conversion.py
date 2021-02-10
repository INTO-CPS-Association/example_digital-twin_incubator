import pandas

from incubator.communication.shared.protocol import from_s_to_ns


def convert_to_results_db(results_dict, params, measurement, tags):

    results_db = []

    time = results_dict["time"]

    def get_row(i):
        row = {}
        for k in results_dict:
            row[k] = results_dict[k][i]
        return row

    for i in range(len(time)):
        point = {
            "measurement": measurement,
            "time": from_s_to_ns(time[i]),
            "tags": tags,
            "fields": get_row(i)
        }
        results_db.append(point)

    return results_db
