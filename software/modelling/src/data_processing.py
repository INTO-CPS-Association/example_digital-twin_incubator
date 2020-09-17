import pandas


def load_data(filepath):
    csv = pandas.read_csv(filepath)
    # normalize time
    csv["time"] = csv["time"] - csv.iloc[0]["time"]
    return csv
