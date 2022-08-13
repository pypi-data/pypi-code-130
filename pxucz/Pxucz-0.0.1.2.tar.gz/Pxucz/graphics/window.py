import glfw
from OpenGL.GL import *

from Pxucz.initial.set_variables import GRAPHICS_FPS_LIMITER
from Pxucz.utils import global_variables


def create_window(window_width: int, window_height: int, window_name: str):
    return glfw.create_window(
        width=window_width,
        height=window_height,
        title=window_name,
        monitor=None,
        share=None,
    )


def set_window_icon(window, image):
    glfw.set_window_icon(window=window, count=1, images=image)


def set_window_aspect_ratio(window, aspect_x, aspect_y):
    glfw.set_window_aspect_ratio(window=window, numer=aspect_x, denom=aspect_y)


def make_context_current(window):
    glfw.make_context_current(window=window)


def window_should_close(window):
    return glfw.window_should_close(window=window)


def window_poll_events():
    return glfw.poll_events()


def destroy_window(window):
    glfw.destroy_window(window=window)


def terminate():
    glfw.terminate()


def Clear(FLAGS):
    glClear(FLAGS)


def swap_buffers(window):
    glfw.swap_buffers(window=window)


def get_time():
    return glfw.get_time()


def swap_interval(interval: int):
    glfw.swap_interval(interval=interval)


def set_fps_limit(fps: int):
    last = global_variables.get_var(name=GRAPHICS_FPS_LIMITER)
    while glfw.get_time() <= last + 1 / fps:
        pass
    global_variables.set_var(name=GRAPHICS_FPS_LIMITER, value=last + 1 / fps)
