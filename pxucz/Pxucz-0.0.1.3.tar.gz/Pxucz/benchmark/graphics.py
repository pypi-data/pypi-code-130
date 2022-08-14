import glfw

from Pxucz.initial.set_variables import BENCHMARK_FRAMECOUNT, BENCHMARK_PREVIOUSTIME
from Pxucz.utils import global_variables


def get_fps():
    framecount = global_variables.get_var(name=BENCHMARK_FRAMECOUNT)
    if glfw.get_time() - global_variables.get_var(name=BENCHMARK_PREVIOUSTIME) >= 1:
        global_variables.set_var(name=BENCHMARK_FRAMECOUNT, value=0)
        global_variables.set_var(name=BENCHMARK_PREVIOUSTIME, value=glfw.get_time())
        return framecount
    global_variables.set_var(name=BENCHMARK_FRAMECOUNT, value=framecount + 1)
