"""Interface for the MDF selection library.

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
from .types import T_ObjectHandle
from .util import singleton
from .wrapper_base import WrapperBase

@singleton
class Selection(WrapperBase):
  """Selection - wrapper for mdf_selection.dll"""
  def __init__(self):
    super().__init__("mdf_selection", "mapteksdk.capi.selection")

  @staticmethod
  def method_prefix():
    return "Selection"

  def capi_functions(self):
    return [
      # Functions changed in version 0.
      # Format:
      # "name" : (return_type, arg_types)
      {"SelectionSaveGlobalSelection" : (T_ObjectHandle, None),
       "SelectionSetGlobalSelection" : (ctypes.c_void_p, [T_ObjectHandle, ]),
       "SelectionFreeSavedSelection" : (ctypes.c_void_p, [T_ObjectHandle, ]),},
      # Functions changed in version 1.
      {"SelectionCApiVersion" : (ctypes.c_uint32, None),
       "SelectionCApiMinorVersion" : (ctypes.c_uint32, None),}
    ]
