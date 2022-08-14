from time import *


# For python version < 3.7
if "time_ns" not in globals():
    __SCALE = 1000000000

    def time_ns():
        return round(__SCALE * time())

    def process_time_ns():
        return round(__SCALE * process_time())

    def perf_counter_ns():
        return round(__SCALE * perf_counter())


def time_ms():
    return int(1000 * time())
