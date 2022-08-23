import time
import builtins


def millis():
    return int((time.perf_counter() - builtins.start_time) * 1000)


def day():
    return int(time.strftime("%d"))


def hour():
    return int(time.strftime("%H"))


def minute():
    return int(time.strftime("%M"))


def second():
    return int(time.strftime("%S"))


def year():
    return int(time.strftime("%Y"))
