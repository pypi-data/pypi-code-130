# auto-generated file
__all__ = ['lib', 'ffi']

import os
from arrow_odbc._native__ffi import ffi

lib = ffi.dlopen(os.path.join(os.path.dirname(__file__), '_native__lib.cp310-win_amd64.pyd'), 0)
del os
