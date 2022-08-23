"""Interface for the MDF preference library.

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
from .util import singleton
from .wrapper_base import WrapperBase

@singleton
class Preference(WrapperBase):
  """Preference - wrapper for mdf_preference.dll"""
  def __init__(self):
    super().__init__("mdf_preference", "mapteksdk.capi.preference")

  @staticmethod
  def method_prefix():
    return "Preference"

  def capi_functions(self):
    return [
      # Functions changed in version 0.
      # Format:
      # "name" : (return_type, arg_types)
      {"PreferenceResetToDefaults" : (ctypes.c_void_p, None),
       "PreferenceCategoryCount" : (ctypes.c_uint32, None),
       "PreferenceGetCategoryName" : (ctypes.c_void_p, [ctypes.c_uint32, ctypes.c_char_p, ctypes.c_uint64, ]),
       "PreferenceGetCategoryEntryCount" : (ctypes.c_uint32, [ctypes.c_uint32, ]),
       "PreferenceGetEntryName" : (ctypes.c_void_p, [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_char_p, ctypes.c_uint64, ]),
       "PreferenceIsBoolean" : (ctypes.c_bool, [ctypes.c_uint32, ctypes.c_uint32, ]),
       "PreferenceGetPreferenceBool" : (ctypes.c_bool, [ctypes.c_uint32, ctypes.c_uint32, ]),
       "PreferenceGetPreferenceJson" : (ctypes.c_void_p, [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_char_p, ctypes.c_uint64, ]),
       "PreferenceSetPreferenceBool" : (ctypes.c_void_p, [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_bool, ]),
       "PreferenceSetPreferenceJson" : (ctypes.c_void_p, [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_char_p, ]),},
      # Functions changed in version 1.
      {"PreferenceCApiVersion" : (ctypes.c_uint32, None),
       "PreferenceCApiMinorVersion" : (ctypes.c_uint32, None),}
    ]
