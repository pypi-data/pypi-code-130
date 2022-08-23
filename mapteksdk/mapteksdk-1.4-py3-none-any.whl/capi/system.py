"""Interface for the MDF system library.

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
class System(WrapperBase):
  """System - wrapper for mdf_system.dll"""
  def __init__(self):
    super().__init__("mdf_system", "mapteksdk.capi.system")

  @staticmethod
  def method_prefix():
    return "System"

  def capi_functions(self):
    return [
      # Functions changed in version 0.
      # Format:
      # "name" : (return_type, arg_types)
      {"SystemFlagInWorkbench" : (ctypes.c_void_p, None),
       "SystemSetApplicationInformation" : (ctypes.c_void_p, [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, ]),
       "SystemSetEtcPath" : (ctypes.c_void_p, [ctypes.c_char_p, ]),
       "SystemSetBinPath" : (ctypes.c_void_p, [ctypes.c_char_p, ]),
       "SystemNotifyEnvironmentChanged" : (ctypes.c_void_p, None),
       "SystemBanEnvironmentUse" : (ctypes.c_void_p, [ctypes.c_char_p, ]),
       "SystemAddToEnvironmentWhiteList" : (ctypes.c_void_p, [ctypes.c_char_p, ]),
       "SystemHostId" : (ctypes.c_int32, [ctypes.c_char_p, ctypes.c_uint32, ]),
       "SystemLogFilePath" : (ctypes.c_int32, [ctypes.c_char_p, ctypes.c_uint32, ]),
       "SystemApplicationLogFilePath" : (ctypes.c_int32, [ctypes.c_char_p, ctypes.c_uint32, ]),
       "SystemBaseConfigurationDirectory" : (ctypes.c_int32, [ctypes.c_char_p, ctypes.c_uint32, ]),
       "SystemApplicationVersionSuffix" : (ctypes.c_int32, [ctypes.c_char_p, ctypes.c_uint32, ]),
       "SystemBranchVersion" : (ctypes.c_int32, [ctypes.c_char_p, ctypes.c_uint32, ]),
       "SystemBuildId" : (ctypes.c_int32, [ctypes.c_char_p, ctypes.c_uint32, ]),
       "SystemApplicationFeatureStrings" : (ctypes.c_int32, [ctypes.c_char_p, ctypes.c_uint32, ]),},
      # Functions changed in version 1.
      {}
    ]
