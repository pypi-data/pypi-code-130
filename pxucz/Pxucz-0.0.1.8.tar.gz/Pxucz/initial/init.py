from Pxucz.initial import set_variables
from Pxucz.initial.set_variables import PXUCZ_ASPECT_Y, PXUCZ_ASPECT_X
from Pxucz.utils import global_path
from Pxucz.initial import opener as px_opener
from Pxucz.utils import global_variables


def init(
    abspath: str, loader_size_x: int, loader_size_y: int, ASPECT_X: int, ASPECT_Y: int
):
    global_path.set_abs_path(path=abspath)
    set_variables.setvar()
    global_variables.set_var(name=PXUCZ_ASPECT_X, value=ASPECT_X)
    global_variables.set_var(name=PXUCZ_ASPECT_Y, value=ASPECT_Y)
    px_opener.start(size_x=loader_size_x, size_y=loader_size_y)
