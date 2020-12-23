ROUTING_KEY_STATE = "incubator.driver.state"
ROUTING_KEY_HEATER = "incubator.hardware.gpio.heater.on"
ROUTING_KEY_FAN = "incubator.hardware.gpio.fan.on"
ENCODING = "ascii"
HEAT_CTRL_QUEUE = "heater_control"
FAN_CTRL_QUEUE = "fan_control"


def convert_str_to_bool(body):
    if body is None:
        return None
    else:
        return body.decode(ENCODING) == "True"
