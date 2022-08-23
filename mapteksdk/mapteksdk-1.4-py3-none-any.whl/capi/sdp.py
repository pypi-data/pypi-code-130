"""Interface for the MDF spatial data processing library.

Warnings
--------
Vendors and clients should not develop scripts or applications against
this module. The contents may change at any time without warning.

"""
###############################################################################
#
# (C) Copyright 2021, Maptek Pty Ltd. All rights reserved.
#
###############################################################################

# pylint: disable=line-too-long
# pylint: disable=invalid-name;reason=Names match C++ names.
import ctypes

from .types import T_ReadHandle
from .util import (singleton, raise_if_version_too_old, CApiUnknownError)

from .wrapper_base import WrapperBase

@singleton
class Sdp(WrapperBase):
  """Sdp - wrapper for mdf_sdp.dll"""
  def __init__(self):
    super().__init__("mdf_sdp", "mapteksdk.capi.sdp")

  @staticmethod
  def method_prefix():
    return "Sdp"

  def capi_functions(self):
    return [
      # Functions changed in version 0.
      # Format:
      # "name" : (return_type, arg_types)
      {},
      # Functions changed in version 1.
      {"SdpCApiVersion" : (ctypes.c_uint32, None),
       "SdpCApiMinorVersion" : (ctypes.c_uint32, None),
       "SdpRasterSetControlMultiPoint" : (ctypes.c_uint8, [ctypes.POINTER(T_ReadHandle), ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_double), ctypes.c_uint32, ]),
      }
    ]

  def CApiVersion(self):
    """Returns the API version for the sdp DLL."""
    raise_if_version_too_old("Spatial data processing", self.version, (1, 3))

    return self.dll.SdpCApiVersion()

  def CApiMinorVersion(self):
    """Returns the minor API version for the sdp DLL."""
    raise_if_version_too_old("Spatial data processing", self.version, (1, 3))

    return self.dll.SdpCApiMinorVersion()

  def RasterSetControlMultiPoint(self, lock, world_points, image_points):
    """Set raster control using the perspective algorithm which takes
    eight or more world and image points.

    Parameters
    ----------
    world_points : numpy.ndarray
      The world points to use to set the control.
    image_points : numpy.ndarray
      The image points to use to set the control.

    """
    raise_if_version_too_old("Multi point raster association",
                             self.version,
                             (1, 3))

    # Use the minimum size as the point count.
    point_count = min(world_points.shape[0], image_points.shape[0])
    if point_count < 8:
      raise ValueError("Multi point association requires at least eight points, "
                       f"given: {point_count}")

    c_image_points = (ctypes.c_double * (point_count * 2))()
    c_image_points[:] = image_points.astype(ctypes.c_double, copy=False).ravel()
    c_world_points = (ctypes.c_double * (point_count * 3))()
    c_world_points[:] = world_points.astype(ctypes.c_double, copy=False).ravel()

    result = self.dll.SdpRasterSetControlMultiPoint(lock,
                                                    c_image_points,
                                                    c_world_points,
                                                    point_count)

    if result == 3:
      raise ValueError("Failed to associate raster: Positioning error")
    if result != 0:
      raise CApiUnknownError("Failed to set multi-point registration")
