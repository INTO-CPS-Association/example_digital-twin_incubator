import pandas

from communication.shared.protocol import from_s_to_ns


def convert_to_results_db(results_dict, params, measurement, tags):

    results_db = []

    time = results_dict["time"]

    # Record a single point with all the parameters
    assert "variability" not in tags
    parameter_tags = tags.copy()
    parameter_tags["variability"] = "parameter"
    tags["variability"] = "variable"
    assert tags["variability"] != parameter_tags["variability"]

    point = {
        "measurement": measurement,
        "time": from_s_to_ns(time[0]),
        "tags": parameter_tags,
        "fields": params
    }
    results_db.append(point)

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
