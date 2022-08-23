"""Interface for the MDF reportwindow library.

Warnings
--------
Vendors and clients should not develop scripts or applications against
this module. The contents may change at any time without warning.

"""
###############################################################################
#
# (C) Copyright 2020, Maptek Pty Ltd. All rights reserved.
#
###############################################################################

# pylint: disable=line-too-long
import ctypes
from .types import T_ContextHandle
from .util import singleton
from .wrapper_base import WrapperBase

@singleton
class ReportWindow(WrapperBase):
  """ReportWindow - wrapper for mdf_reportwindow.dll"""
  def __init__(self):
    super().__init__("mdf_reportwindow", "mapteksdk.capi.reportwindow")

  @staticmethod
  def method_prefix():
    return "ReportWindow"

  def capi_functions(self):
    return [
      # Functions changed in version 0.
      # Format:
      # "name" : (return_type, arg_types)
      {"ReportWindowInitialise" : (ctypes.c_void_p, [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_void_p, ]),
       "ReportWindowFinalise" : (ctypes.c_void_p, None),
       "ReportWindowSetPlaceholderIcons" : (ctypes.c_void_p, [ctypes.c_char_p, ctypes.c_char_p, ]),
       "ReportWindowNewContext" : (T_ContextHandle, None),
       "ReportWindowHandleClick" : (ctypes.c_void_p, [ctypes.c_char_p, ]),
       "ReportWindowHandleDoubleClick" : (ctypes.c_void_p, [ctypes.c_char_p, ]),
       "ReportWindowHandleContextMenu" : (ctypes.c_void_p, [ctypes.c_char_p, ]),
       "ReportWindowHandleStartDrag" : (ctypes.c_void_p, [ctypes.c_char_p, ]),
       "ReportWindowUpdatePathReference" : (ctypes.c_void_p, [ctypes.c_char_p, ctypes.c_uint32, ctypes.c_char_p, ]),
       "ReportWindowUpdateObjectReference" : (ctypes.c_void_p, [ctypes.c_char_p, ctypes.c_uint32, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_bool, ctypes.c_bool, ]),},
      # Functions changed in version 1.
      {"ReportWindowCApiVersion" : (ctypes.c_uint32, None),
       "ReportWindowCApiMinorVersion" : (ctypes.c_uint32, None),}
    ]
