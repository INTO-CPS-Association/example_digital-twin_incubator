import logging
import pandas

from incubator.communication.shared.protocol import from_ns_to_s


def query(query_api, bucket, start_date_ns, end_date_ns, measurement, field):
    _l = logging.getLogger("IncubatorDataQuery")

    _l.debug("Query: ")
    query_to_be = f"""
        from(bucket: "{bucket}")
          |> range(start: time(v: {start_date_ns}), stop: time(v: {end_date_ns}))
          |> filter(fn: (r) => r["_measurement"] == "{measurement}")
          |> filter(fn: (r) => r["_field"] == "{field}")
          |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
        """
    _l.debug(query_to_be)
    result = query_api.query_data_frame(query_to_be)
    assert isinstance(result, pandas.DataFrame), f"Result is not a dataframe. " \
                                                 f"Instead, the following object of type {type(result)} " \
                                                 f"has been returned: {result}. " \
                                                 f"Maybe the database has an inconsistent set of records for the " \
                                                 f"same measurement. For instance, the tags might be different, " \
                                                 f"or the type of values is different."
    _l.debug(f"New query for {measurement}'s {field}: {len(result)} samples retrieved.")
    return result


def query_most_recent_fields(query_api, bucket, start_date_ns, n_records, measurements, fields):
    _l = logging.getLogger("IncubatorDataQuery")

    measurements_filter = ' or '.join([f'r["_measurement"] == "{m}"' for m in measurements])
    fields_filter = ' or '.join([f'r["_field"] == "{f}"' for f in fields])

    _l.debug("query_most_recent_fields: ")
    query_to_be = f"""
            from(bucket: "{bucket}")
              |> range(start: time(v: {start_date_ns}))
              |> filter(fn: (r) => {measurements_filter})
              |> filter(fn: (r) => {fields_filter})
              |> sort(columns: ["_time"], desc: true)
              |> limit(n:{n_records})
            """
    _l.debug(query_to_be)
    result = query_api.query_data_frame(query_to_be)
    assert isinstance(result, pandas.DataFrame), f"Result is not a dataframe. " \
                                                 f"Instead, the following object of type {type(result)} " \
                                                 f"has been returned: {result}. " \
                                                 f"Maybe the database has an inconsistent set of records for the " \
                                                 f"same measurement.  For instance, the tags might be different, " \
                                                 f"or the type of values is different."
    _l.debug(f"New query for {measurements} and {fields}: {len(result)} samples retrieved.")
    return result


def query_convert_aligned_data(query_api, bucket, start_date_ns, end_date_ns, measurement_fields):
    assert start_date_ns <= end_date_ns
    _l = logging.getLogger("IncubatorDataQuery")

    _l.debug("Querying given measurement fields.")
    _l.debug(measurement_fields)
    first_measurement = None
    first_measurement_name = None
    first_measurement_field = None
    raw_data = {}
    for measurement in measurement_fields:
        raw_data[measurement] = {}
        for field in measurement_fields[measurement]:
            raw_data[measurement][field] = query(query_api, bucket, start_date_ns, end_date_ns, measurement, field)
            assert not raw_data[measurement][field].empty, f"Query returned no data: ."
            if first_measurement is None:
                first_measurement_name = measurement
                first_measurement_field = field
                first_measurement = raw_data[measurement][field]

    assert first_measurement is not None, "At least one measurement and field must be provided."

    # I've observed from experience that there are small numerical errors in the timestamps stored by influxdb.
    # We could choose this value as a function of the system sampling size. That would be at least 3 seconds.
    # Right now a precision of ms seems to be a good choice.
    TIMESTAMP_TOLERANCE = 1e-3

    _l.debug("Ensuring retrieved data is consistent.")
    ground_truth_t = first_measurement["_time"]
    for measurement in measurement_fields:
        for field in measurement_fields[measurement]:
            t = raw_data[measurement][field]["_time"]
            if not (len(t) == len(ground_truth_t)):
                msg = f"Retrieved data is inconsistent: " \
                      f"Measure {first_measurement_name} has {len(ground_truth_t)} samples, " \
                      f"but {measurement} has {len(t)} samples."
                _l.error(msg)
                raise ValueError(msg)
            for i in range(len(t)):
                aligned = abs((ground_truth_t.iloc[i] - t.iloc[i]).total_seconds()) < TIMESTAMP_TOLERANCE
                if not aligned:
                    msg = f"Found at least two timestamps that are not aligned by less than {TIMESTAMP_TOLERANCE}: " \
                          f"{first_measurement_name}.{first_measurement_field}({ground_truth_t.iloc[i]}) " \
                          f"is not aligned with {measurement}.{field}({t.iloc[i]})."
                    _l.error(msg)
                    raise ValueError(msg)

    _l.debug("Converting timestamps to seconds.")
    # convert start and end dates to seconds
    # This is needed because the simulations run in seconds.
    start_date_s = from_ns_to_s(start_date_ns)
    end_date_s = from_ns_to_s(end_date_ns)

    # Convert raw_data into format that simulation _plant can take
    time_seconds = first_measurement.apply(lambda row: row["_time"].timestamp(), axis=1).to_numpy()

    _l.debug("Check that data start and end intervals are coherent.")
    # The following is true because of the query we made at the db
    # The tolerance factor is because of numerical rounding issues.
    assert time_seconds[0] + TIMESTAMP_TOLERANCE >= start_date_s and \
           time_seconds[-1] <= end_date_s + TIMESTAMP_TOLERANCE, \
        f"Query between dates {start_date_s} and {end_date_s} produced incoherent timestamps from the db. " \
        f"The initial timestamp found is {time_seconds[0]} and final timestamp is {time_seconds[-1]}. " \
        f"The corresponding differences (which should have been positive) are {time_seconds[0] - start_date_s} and {end_date_s - time_seconds[-1]}."

    _l.debug("Converting data to numpy.")
    result_data = {}
    for measurement in measurement_fields:
        result_data[measurement] = {}
        for field in measurement_fields[measurement]:
            result_data[measurement][field] = raw_data[measurement][field][field].to_numpy()

    return time_seconds, result_data
