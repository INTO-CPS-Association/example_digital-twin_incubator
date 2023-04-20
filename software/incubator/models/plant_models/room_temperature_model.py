import math


def room_temperature(t):
    """
    Rough _plant of room temperature
    Expects time in seconds since EPOCH.
    """
    a = 10.0
    b = 10000.0
    c = 15.0
    d = 2.7
    return a * math.sin(t / b - d) + c