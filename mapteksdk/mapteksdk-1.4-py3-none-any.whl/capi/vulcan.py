"""Interface for the MDF vulcan library.

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
class Vulcan(WrapperBase):
  """Vulcan - wrapper for mdf_vulcan.dll"""
  def __init__(self):
    super().__init__("mdf_vulcan", "mapteksdk.capi.vulcan")

  @staticmethod
  def method_prefix():
    return "Vulcan"

  def capi_functions(self):
    return [
      # Functions changed in version 0.
      # Format:
      # "name" : (return_type, arg_types)
      {"VulcanErrorMessage" : (ctypes.c_char_p, []),
       "VulcanRead00tFile" : (T_ObjectHandle, [ctypes.c_char_p, ctypes.c_int32]),
       "VulcanWrite00tFile" : (ctypes.c_bool, [T_ObjectHandle, ctypes.c_char_p, ctypes.c_int32]),
       "VulcanReadBmfFile" : (T_ObjectHandle, [ctypes.c_char_p, ctypes.c_int32]),
       "VulcanWriteBmfFile" : (ctypes.c_bool, [T_ObjectHandle, ctypes.c_char_p, ctypes.c_int32]),},
      # Functions changed in version 1.
      {"VulcanCApiVersion" : (ctypes.c_uint32, None),
       "VulcanCApiMinorVersion" : (ctypes.c_uint32, None),}
    ]
