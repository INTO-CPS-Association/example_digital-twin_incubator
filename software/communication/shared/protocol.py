import json

ROUTING_KEY_STATE = "incubator.record.driver.state"
ROUTING_KEY_CONTROLLER = "incubator.record.controller.state"
ROUTING_KEY_RECORDER = "incubator.record.#"
ROUTING_KEY_HEATER = "incubator.hardware.gpio.heater.on"
ROUTING_KEY_FAN = "incubator.hardware.gpio.fan.on"
ROUTING_KEY_PTSIMULATOR4 = "incubator.simulator.physicaltwin.4params"
ROUTING_KEY_PLANTSIMULATOR4 = "incubator.simulator.plant.4params"
ROUTING_KEY_PLANTCALIBRATOR4 = "incubator.calibrator.plant.4params"
ROUTING_KEY_KFPLANTSERVER = "incubator.monitor.plant.4params"
ENCODING = "ascii"


def convert_str_to_bool(body):
    if body is None:
        return None
    else:
        return body.decode(ENCODING) == "True"


def encode_json(object):
    return json.dumps(object).encode(ENCODING)


def decode_json(bytes):
    return json.loads(bytes.decode(ENCODING))


def from_ns_to_s(time_ns):
    return time_ns / 1e9


def from_s_to_ns(time_s):
    return int(time_s * 1e9)