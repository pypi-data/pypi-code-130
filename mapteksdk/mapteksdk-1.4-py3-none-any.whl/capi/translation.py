"""Interface for the MDF translation library.

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
# pylint: disable=invalid-name;reason=Names match C++ names.
import ctypes
from .types import T_TextHandle, T_ContextHandle
from .util import (singleton, raise_if_version_too_old, get_string)
from .wrapper_base import WrapperBase

@singleton
class Translation(WrapperBase):
  """Translation - wrapper for mdf_translation.dll"""
  def __init__(self):
    super().__init__("mdf_translation", "mapteksdk.capi.translation")

  @staticmethod
  def method_prefix():
    return "Translation"

  def capi_functions(self):
    return [
      # Functions changed in version 0.
      # Format:
      # "name" : (return_type, arg_types)
      {"TranslationSetCallbacks" : (ctypes.c_void_p, [ctypes.c_uint32, ]),
       "TranslationNewEmptyText" : (T_TextHandle, None),
       "TranslationNewText" : (T_TextHandle, [ctypes.c_char_p, ]),
       "TranslationFromSerialisedString" : (T_TextHandle, [ctypes.c_char_p, ]),
       "TranslationFreeText" : (ctypes.c_void_p, [T_TextHandle, ]),
       "TranslationIsEmpty" : (ctypes.c_bool, [T_TextHandle, ]),
       "TranslationTextEqual" : (ctypes.c_bool, [T_TextHandle, T_TextHandle, ]),
       "TranslationTranslate" : (ctypes.c_uint32, [T_TextHandle, ctypes.c_char_p, ctypes.c_uint32, ]),
       "TranslationTranslateWithContext" : (ctypes.c_uint32, [T_TextHandle, T_ContextHandle, ctypes.c_char_p, ctypes.c_uint32, ]),
       "TranslationTranslateInEnglish" : (ctypes.c_uint32, [T_TextHandle, ctypes.c_char_p, ctypes.c_uint32, ]),
       "TranslationNewMenuContext" : (T_ContextHandle, None),
       "TranslationFreeContext" : (ctypes.c_void_p, [T_ContextHandle, ]),
       "TranslationAddArgumentString" : (ctypes.c_void_p, [T_TextHandle, ctypes.c_char_p, ]),
       "TranslationAddArgumentText" : (ctypes.c_void_p, [T_TextHandle, T_TextHandle, ]),
       "TranslationAddArgumentFloat" : (ctypes.c_void_p, [T_TextHandle, ctypes.c_float, ]),
       "TranslationAddArgumentDouble" : (ctypes.c_void_p, [T_TextHandle, ctypes.c_double, ]),
       "TranslationSetPrimaryLanguageIdentifier" : (ctypes.c_void_p, [ctypes.c_char_p, ]),
       "TranslationSetSecondaryLanguageIdentifier" : (ctypes.c_void_p, [ctypes.c_char_p, ]),},
      # Functions changed in version 1.
      {"TranslationCApiVersion" : (ctypes.c_uint32, None),
       "TranslationCApiMinorVersion" : (ctypes.c_uint32, None),
       "TranslationToSerialisedString" : (ctypes.c_uint32, [T_TextHandle, ctypes.c_char_p, ctypes.c_uint32, ]),
       }
    ]

  def ToSerialisedString(self, text_handle):
    """Convert the text object into a serialised string.

    This serialised string is suitable for storage in memory to converted back
    to a text object by FromSerialisedString().

    Parameters
    ----------
    text_handle : T_TextHandle
      The handle for the text.

    Raises
    ------
    CApiFunctionNotSupportedError
      If the application is too old to support this function.
    """
    raise_if_version_too_old("Working with translatable text",
                             current_version=self.version,
                             required_version=(1, 3))

    return get_string(text_handle, self.dll.TranslationToSerialisedString)
