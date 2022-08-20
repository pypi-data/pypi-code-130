import functools
from typing import Callable

try:
    # python >= 3.10
    from collections.abc import Sequence
except ImportError:
    # python <= 3.9
    from collections import Sequence  # type: ignore[import,attr-defined,no-redef]

try:
    import colormath  # type: ignore[import]

    HAS_COLORMATH = True
except ImportError:
    HAS_COLORMATH = False

if HAS_COLORMATH:
    from colormath.color_objects import sRGBColor, LabColor  # type: ignore[import,no-redef]
    from colormath.color_conversions import convert_color  # type: ignore[import,no-redef]


def require_colormath():
    if not HAS_COLORMATH:
        raise RuntimeError('Installation of the colormath library is required to use this feature.')


def requires_colormath(fn: Callable) -> Callable:
    @functools.wraps(fn)
    def wrapped(*args, **kwargs):
        require_colormath()
        return fn(*args, **kwargs)

    return wrapped
