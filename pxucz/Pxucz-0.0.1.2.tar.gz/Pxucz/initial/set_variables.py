import glfw
from Pxucz.utils import global_variables
BENCHMARK_PREVIOUSTIME = "PXUCZ_BENCHMARK_FPS_PREVIOUS_TIME_VAR"
BENCHMARK_FRAMECOUNT = "PXUCZ_BENCHMARK_FPS_COUNT_ER_VAR"
GRAPHICS_FPS_LIMITER = "PXUCZ_FPS_RATE_LIMITER_TIME_VAR"


def setvar():
    global_variables.set_var(name=GRAPHICS_FPS_LIMITER, value=glfw.get_time())
    global_variables.set_var(name=BENCHMARK_FRAMECOUNT, value=0)
    global_variables.set_var(name=BENCHMARK_PREVIOUSTIME, value=glfw.get_time())
