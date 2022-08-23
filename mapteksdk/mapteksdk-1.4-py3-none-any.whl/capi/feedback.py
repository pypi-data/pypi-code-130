"""Interface for the MDF feedback library.

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
from .types import T_ReadHandle
from .util import singleton
from .wrapper_base import WrapperBase

@singleton
class Feedback(WrapperBase):
  """Feedback - wrapper for mdf_feedback.dll"""
  def __init__(self):
    super().__init__("mdf_feedback", "mapteksdk.capi.feedback")

  @staticmethod
  def method_prefix():
    return "Feedback"

  def capi_functions(self):
    return [
      # Functions changed in version 0.
      # Format:
      # "name" : (return_type, arg_types)
      {"FeedbackPrepareReport" : (ctypes.POINTER(T_ReadHandle), [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_void_p, ctypes.c_uint32, ]),
       "FeedbackSendReport" : (ctypes.c_bool, [ctypes.POINTER(T_ReadHandle), ]),
       "FeedbackSaveAsZip" : (ctypes.c_bool, [ctypes.POINTER(T_ReadHandle), ctypes.c_char_p, ]),
       "FeedbackCancelReport" : (ctypes.c_void_p, [ctypes.POINTER(T_ReadHandle), ]),
       "FeedbackTakeScreenshotAndAppend" : (ctypes.c_void_p, [ctypes.POINTER(T_ReadHandle), ]),},
      # Functions changed in version 1.
      {"FeedbackCApiVersion" : (ctypes.c_uint32, None),
       "FeedbackCApiMinorVersion" : (ctypes.c_uint32, None),}
    ]
