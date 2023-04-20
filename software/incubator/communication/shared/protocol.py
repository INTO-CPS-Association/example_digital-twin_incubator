import json

ENCODING = "ascii"

ROUTING_KEY_STATE = "incubator.record.driver.state"
ROUTING_KEY_UPDATE_CTRL_PARAMS = "incubator.update.open_loop_controller.parameters"
ROUTING_KEY_COSIM_PARAM = "incubator.cosim.controller.parameters"
ROUTING_KEY_CONTROLLER = "incubator.record.controller.state"
ROUTING_KEY_HEATER = "incubator.hardware.gpio.heater.on"
ROUTING_KEY_FAN = "incubator.hardware.gpio.fan.on"


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


def from_s_to_ns_array(time_s):
    ns_floats = time_s * 1e9
    ns_ints = ns_floats.astype(int)
    return ns_ints
