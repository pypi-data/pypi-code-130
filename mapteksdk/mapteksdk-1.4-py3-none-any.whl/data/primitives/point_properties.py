"""Support for point primitives.

A point is a 3D location in space. In Python, they are represented as a
numpy array containing three 64-bit floating point numbers, representing
the location relative to the origin. For example, the point [X, Y, Z]
is X metres away from the origin in the x direction (typically east),
Y metres away from the origin in the y direction (typically north)
and Z metres away from the origin in the z direction (typically up).

Points are typically used to define other primitives, such as edges, facets
and cells.

"""
###############################################################################
#
# (C) Copyright 2020, Maptek Pty Ltd. All rights reserved.
#
###############################################################################

import ctypes
import logging

import numpy as np

from .primitive_attributes import PrimitiveAttributes, PrimitiveType
from ..errors import CannotSaveInReadOnlyModeError, DegenerateTopologyError
from ...common import (trim_pad_1d_array, trim_pad_2d_array,
                       convert_array_to_rgba)
from ...internal.lock import WriteLock

log = logging.getLogger("mapteksdk.data")

# The following warning can be enabled if the <Primitive>Properties classes
# ended in Mixin as then pylint expects that the members are defined elsewhere.
# pylint: disable=no-member

class PointProperties:
  """Mixin class which provides spatial objects support for point primitives.

  A point is represented as a numpy array of length 3 of the form
  [x, y, z] where x, y and z are floating point numbers.
  For example, the point [1, 2, 3.5] is 1 metre away from the origin in the X
  direction (East in a standard view), 2 units away from the origin in the
  Y direction (North in a standard view) and 3.5 units away from the origin in
  the z direction.
  If one of the elements of a point is negative, this indicates its
  distance from the origin is in the opposite direction. For example,
  the point [-1, 0, 0] is 1 unit away from the origin in the direction
  opposite to the East arrow.

  Functions and properties defined on this class are available on all
  classes which support points.

  """
  __points = None
  __point_colours = None
  __point_selection = None
  __point_visibility = None
  __point_attributes = None
  __point_z = None

  @property
  def points(self):
    """A 2D ndarray of points of the form:
    [[x1, y1, z1], [x2, y2, z2], ..., [xN, yN, zN]]
    Where N is the number of points.

    Raises
    ------
    AttributeError
      If attempting to set the points on an object which does not support
      setting points.

    Examples
    --------
    Create a new point set and set the points:

    >>> from mapteksdk.project import Project
    >>> from mapteksdk.data import PointSet
    >>> project = Project()
    ... with project.new("cad/test_points", PointSet) as new_points:
    ...     new_points.points = [[0, 0, 0], [1, 0, 0], [1, 1, 0],
    ...                          [0, 1, 0], [0, 2, 2], [0, -1, 3]]

    Print the second point from the point set defined above.

    >>> from mapteksdk.project import Project
    >>> from mapteksdk.data import PointSet
    >>> project = Project()
    >>> with project.read("cad/test_points") as read_points:
    ...     print(read_points.points[2])
    [1., 1., 0.]

    Then set the 2nd point to [1, 2, 3]:

    >>> from mapteksdk.project import Project
    >>> from mapteksdk.data import PointSet
    >>> project = Project()
    >>> with project.edit("cad/test_points") as edit_points:
    ...     edit_points.points[2] = [1, 2, 3]

    Iterate over all of the points and print them.

    >>> from mapteksdk.project import Project
    >>> from mapteksdk.data import PointSet
    >>> project = Project()
    >>> with project.read("cad/test_points") as read_points:
    >>>     for point in read_points.points:
    >>>         print(point)
    [0., 0., 0.]
    [1., 0., 0.]
    [1., 2., 3.]
    [0., 1., 0.]
    [0., 2., 2.]
    [0., -1., 3.]

    Print all points with y > 0 using numpy. Note that index has one
    element for each point which will be true if that point has y > 0
    and false otherwise. This is then used to retrieve the points with
    y > 0.

    >>> from mapteksdk.project import Project
    >>> from mapteksdk.data import PointSet
    >>> project = Project()
    >>> with project.read("cad/test_points") as read_points:
    ...     index = read_points.points[:, 1] > 0
    ...     print(read_points.points[index])
    [[1. 2. 3.]
     [0. 1. 0.]
     [0. 2. 2.]]

    """
    if self.__points is None:
      self.__points = self._get_points()
      # :TRICKY: 2021-12-13
      # For most objects, this is effectively:
      # self.point_count == self.point_count.
      # This case is primarily important for Scans and other objects which
      # overwrite the point count so that it is not equal to the size of the
      # first axis of the points.
      if self.__points.shape[0] != self.point_count:
        self.__points = trim_pad_2d_array(
          self.__points, self.point_count, 3, np.nan)
    return self.__points

  @points.setter
  def points(self, points):
    if not self._can_set_points:
      raise AttributeError("Setting points is disabled for this object.")
    if points is None:
      self.__points = None
    else:
      # Allow for list or ndarray as input
      self.__points = trim_pad_2d_array(points, -1, 3, 0).astype(
        ctypes.c_double)

  @property
  def point_z(self):
    """The Z coordinates of the points.

    Raises
    ------
    ValueError
      If set using a string which cannot be converted to a float.
    ValueError
      If set to a value which cannot be broadcast to the right shape.
    TypeError
      If set using a value which cannot be converted to a float.

    """
    if self.__point_z is None or \
        not np.may_share_memory(self.points, self.__point_z):
      self.__point_z = self.points[:][:, 2]
    return self.__point_z

  @point_z.setter
  def point_z(self, new_z):
    self.point_z[:] = new_z

  @property
  def _can_set_points(self):
    """Returns True if the points of this object can be changed when it
    is opened with project.edit() or project.new().

    Returns
    -------
    bool
      True if points are settable, False otherwise.

    """
    return True

  @property
  def point_colours(self):
    """The colours of the points, represented as a 2d ndarray of RGBA colours.
    When setting the colour you may use RGB or greyscale colours instead of RGBA
    colours.
    The array has one colour for each point. Object.point_colours[i] returns
    the colour of Object.points[i].

    Notes
    -----
    When the point colours are set, if there are more colours than
    points then the excess colours are silently ignored. If there
    are fewer colours than points then uncoloured points are coloured green.
    If only a single colour is specified, instead of padding with green
    all of the points are coloured with that colour.
    i.e.: object.point_colours = [[Red, Green, Blue]] will set all points to be
    the colour [Red, Green, Blue].

    """
    if self.__point_colours is None:
      self.__point_colours = self._get_point_colours()

    if self.__point_colours.shape[0] != self.point_count:
      self.__point_colours = convert_array_to_rgba(self.__point_colours,
                                                   self.point_count)

    return self.__point_colours

  @point_colours.setter
  def point_colours(self, point_colours):
    if point_colours is None:
      self.__point_colours = point_colours
    else:
      if len(point_colours) != 1:
        self.__point_colours = convert_array_to_rgba(point_colours,
                                                     self.point_count)
      else:
        self.__point_colours = convert_array_to_rgba(
          point_colours, self.point_count,
          point_colours[0])

  @property
  def point_visibility(self):
    """A 1D ndarray representing the visibility of points.

    Object.point_visibility[i] is true if Object.point[i] is visible. It will
    be False if the point is invisible.

    Object.point_visibility[i] = False will make Object.point[i]
    invisible.

    """
    if self.__point_visibility is None:
      self.__point_visibility = self._get_point_visibility()

    if len(self.__point_visibility) != self.point_count:
      self.__point_visibility = trim_pad_1d_array(
        self.__point_visibility, self.point_count, True).astype(
          ctypes.c_bool)

    return self.__point_visibility

  @point_visibility.setter
  def point_visibility(self, point_visibility):
    if point_visibility is None:
      self.__point_visibility = point_visibility
    else:
      self.__point_visibility = trim_pad_1d_array(
        point_visibility, self.point_count, True).astype(
          ctypes.c_bool)

  @property
  def point_selection(self):
    """A 1D ndarray representing the point selection.

    If Object.point_selection[i] = True then Object.point[i] is selected.
    Object.point_selection[i] = False then Object.point[i] is not selected.

    """
    if self.__point_selection is None:
      self.__point_selection = self._get_point_selection()

    if len(self.__point_selection) != self.point_count:
      self.__point_selection = trim_pad_1d_array(
        self.__point_selection, self.point_count, False).astype(
          ctypes.c_bool)

    return self.__point_selection

  @point_selection.setter
  def point_selection(self, point_selection):
    if point_selection is None:
      self.__point_selection = point_selection
    else:
      self.__point_selection = trim_pad_1d_array(
        point_selection[:], self.point_count, False).astype(
          ctypes.c_bool)

  @property
  def point_count(self):
    """The number of points in the object."""
    # If points haven't been loaded, load point count from
    # the Project. Otherwise derive it.
    if self.__points is None:
      return self._get_point_count()
    return self.points.shape[0]

  def _invalidate_properties(self):
    """Invalidates the cached point properties. The next time one is requested
    its values will be loaded from the project.

    """
    self.__points = None
    self.__point_colours = None
    self.__point_selection = None
    self.__point_visibility = None
    self.__point_attributes = None
    self.__point_z = None

  def _save_point_properties(self):
    """Save the point properties.

    This must be called during save() of the inheriting object.
    This should never be called directly. To save an object, call save()
    instead.

    Raises
    ------
    CannotSaveInReadOnlyModeError
      If in read-only mode.

    """
    if isinstance(self._lock, WriteLock):
      # Write all relevant properties for this primitive type.
      if self._can_set_points:
        if self.point_count == 0:
          message = "Object must contain at least one point."
          raise DegenerateTopologyError(message)
        if self.__points is not None:
          self._save_points(self.points)

      if self.__point_colours is not None:
        self._save_point_colours(self.point_colours)

      if self.__point_visibility is not None:
        self._save_point_visibility(self.point_visibility)

      if self.__point_selection is not None:
        self._save_point_selection(self.point_selection)

      if self.__point_attributes is not None:
        self.__point_attributes.save_attributes()
    else:
      error = CannotSaveInReadOnlyModeError()
      log.error(error)
      raise error

  @property
  def point_attributes(self):
    """Access the custom point attributes. These are arrays of values
    of the same type with one value for each point.

    Use Object.point_attributes[attribute_name] to access the point attribute
    called attribute_name. See PrimitiveAttributes for valid operations
    on point attributes.

    Returns
    -------
    PrimitiveAttributes
      Access to the point attributes.

    Raises
    ------
    ValueError
      If the type of the attribute is not supported.

    """
    if self.__point_attributes is None:
      self.__point_attributes = PrimitiveAttributes(PrimitiveType.POINT, self)
    return self.__point_attributes

  def save_point_attribute(self, attribute_name, data):
    """Create and/or edit the values of the point attribute attribute_name.

    This is equivalent to Object.point_attributes[attribute_name] = data.

    Parameters
    ----------
    attribute_name : str
      The name of attribute
    data : array_like
      An array_like of length point_count containing the values
      for attribute_name.

    Raises
    ------
    Exception
      If the object is opened in read-only mode.
    ValueError
      If the type of the attribute is not supported.

    """
    self.point_attributes[attribute_name] = data

  def delete_point_attribute(self, attribute_name):
    """Delete a point attribute by name.

    This is equivalent to: point_attributes.delete_attribute(attribute_name)

    Parameters
    ----------
    attribute_name : str
      The name of attribute

    Raises
    ------
    Exception
      If the object is opened in read-only mode.
    ValueError
      If the primitive type is not supported.

    """
    self.point_attributes.delete_attribute(attribute_name)

# pylint: disable=too-few-public-methods
class PointDeletionProperties:
  """Mixin class which adds functionality for removing points.

  This is intended to be used in addition to PointProperties. It is a separate
  class because not all objects which have points support remove_points.
  """
  def remove_points(self, point_indices):
    """Remove one or more points from the object.

    Calling this function is preferable to altering the points array because
    this function also removes the point properties associated with the removed
    points (e.g. point colours, point visibility, etc).

    This operation is performed directly on the Project and will not be undone
    if an error occurs.

    Parameters
    ----------
    point_indices : array_like or int
      The index of the point to remove or a list of indices of points to
      remove.
      Any index which is lower than zero or greater than or equal to the
      point count is ignored (i.e. Passing -1 will not delete the last
      point).

    Returns
    -------
    bool
      If passed a single point index, True if the point was removed
      and False if it was not removed.
      If passed an iterable of point indices, True if the object supports
      removing points and False otherwise.

    Raises
    ------
    ReadOnlyError
      If called on an object not open for editing. This error indicates an
      issue with the script and should not be caught.

    Warnings
    --------
    Any unsaved changes to the object when this function is called are
    discarded before any points are deleted. If you wish to keep these changes,
    call save() before calling this function.

    Examples
    --------
    Deleting a point through this function is preferable over removing the
    point from the points array because this function also deletes the
    properties associated with the deleted points. For example, all points
    will remain the same colour after the deletion operation, which points
    are visible will remain the same, etc. This is shown in the following
    script:

    >>> from mapteksdk.project import Project
    >>> from mapteksdk.data import PointSet
    >>> project = Project()
    >>> red = [255, 0, 0, 255]
    >>> blue = [0, 0, 255, 255]
    >>> with project.new("cad/deletion_example", PointSet) as point_set:
    ...     point_set.points = [[0, 0, 0], [1, 0, 0], [0, 1, 0], [1, 1, 0]]
    ...     point_set.point_colours = [red, red, blue, blue]
    ...     point_set.point_attributes["attribute"] = [0, 1, 2, 3]
    >>> with project.edit(point_set.id) as edit_set:
    ...     edit_set.remove_points((1, 2))
    ...     print("points\\n", edit_set.points)
    ...     print("colours\\n", edit_set.point_colours)
    ...     print("attribute\\n", edit_set.point_attributes["attribute"])
    points
     [[0. 0. 0.]
     [1. 1. 0.]]
    colours
     [[255   0   0 255]
     [  0   0 255 255]]
    attribute
     [0 3]

    """
    self._invalidate_properties()
    if isinstance(point_indices, int):
      remove_request = self._remove_point(point_indices)
    else:
      remove_request = self._remove_points(point_indices)
    self._reconcile_changes()
    return remove_request
