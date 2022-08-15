import threading

import glfw
from OpenGL.GL import *
from Pxucz.initial.set_variables import (
    GRAPHICS_FPS_LIMITER,
    INITIAL_LOADER_TEXT,
    INITIAL_LOADER_CLOSE,
    PXUCZ_ASPECT_X,
    PXUCZ_ASPECT_Y,
)
from Pxucz.utils import global_variables


def create_window(
    window_width: int, window_height: int, window_name: str, fullscreen: bool
):
    glfw.window_hint(glfw.RESIZABLE, glfw.FALSE)
    glfw.window_hint(glfw.VISIBLE, glfw.FALSE)
    glfw.window_hint(glfw.DOUBLEBUFFER, glfw.TRUE)
    glfw.window_hint(glfw.DECORATED, glfw.FALSE)
    global_variables.set_var(
        name=INITIAL_LOADER_TEXT,
        value=f"WINDOW = ({window_width}, {window_height}), TITLE={window_name}",
    )
    if fullscreen:
        return (
            glfw.create_window(
                width=glfw.get_video_mode(glfw.get_primary_monitor())[0][0],
                height=glfw.get_video_mode(glfw.get_primary_monitor())[0][1],
                title=window_name,
                monitor=glfw.get_primary_monitor(),
                share=None,
            ),
            window_width,
            window_height,
        )
    else:
        return (
            glfw.create_window(
                width=window_width,
                height=window_height,
                title=window_name,
                monitor=None,
                share=None,
            ),
            window_width,
            window_height,
        )


def set_window_icon(window, image):
    glfw.set_window_icon(window=window, count=1, images=image)


def set_window_aspect_ratio(window):
    global_variables.set_var(
        name=INITIAL_LOADER_TEXT,
        value=f"WINDOW_ASPECT = ({global_variables.get_var(PXUCZ_ASPECT_X)}, {global_variables.get_var(PXUCZ_ASPECT_Y)})",
    )
    glfw.set_window_aspect_ratio(
        window=window,
        numer=global_variables.get_var(PXUCZ_ASPECT_X),
        denom=global_variables.get_var(PXUCZ_ASPECT_Y),
    )


def make_context_current(window):
    glfw.make_context_current(window=window)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)


def window_should_close(window):
    return glfw.window_should_close(window=window)


def destroy_window(window):
    glfw.destroy_window(window=window)


def terminate():
    glfw.terminate()


def set_fps_limit(fps: int):
    last = global_variables.get_var(name=GRAPHICS_FPS_LIMITER)
    while glfw.get_time() <= last + 1 / fps:
        pass
    global_variables.set_var(name=GRAPHICS_FPS_LIMITER, value=last + 1 / fps)


def task_start(window):
    glfw.show_window(window=window)
    global_variables.set_var(name=INITIAL_LOADER_TEXT, value=INITIAL_LOADER_CLOSE)
