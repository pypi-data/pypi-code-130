"""Functions for importing and exporting data."""
###############################################################################
#
# (C) Copyright 2020, Maptek Pty Ltd. All rights reserved.
#
###############################################################################

from __future__ import annotations
import logging
import pathlib

from ..capi import DataEngine, Vulcan
from .base import DataObject
from .facets import Surface
from .objectid import ObjectID
from .primitives.block_properties import BlockProperties
from .units import DistanceUnit
from ..internal.util import default_type_error_message

log = logging.getLogger("mapteksdk.data.io")

def import_00t(
  path: str | pathlib.Path,
  unit: DistanceUnit=DistanceUnit.METRE) -> ObjectID[Surface]:
  """Import a Maptek Vulcan Triangulation file (00t) into the project.

  Parameters
  ----------
  path
    Path to file to import.
  unit
    The unit used when exporting the file.

  Returns
  -------
  ObjectID
    The ID of the imported object.

  Raises
  ------
  FileNotFoundError
    If the file does not exist.
  TypeError
    If path cannot be converted to a pathlib.Path.
    If the unit is not an instance of DistanceUnit.
  RuntimeError
    If there is a problem importing the file.

  Notes
  -----
  The imported object is not automatically placed inside a container.
  A call to project.add_object() is required to add it to a container.

  """
  log.info("Importing Vulcan Triangulation (00t): %s", path)

  if not isinstance(path, pathlib.Path):
    path = pathlib.Path(path)

  if not isinstance(unit, DistanceUnit):
    raise TypeError(default_type_error_message("unit", unit, DistanceUnit))

  if not path.is_file():
    raise FileNotFoundError(f"Could not find file: {path}")

  imported_object = Vulcan().Read00tFile(
    str(path).encode("utf-8"), unit.value)

  if imported_object.value == 0:
    message = Vulcan().ErrorMessage().decode('utf-8')
    log.error(
      "A problem occurred when importing the 00t: %s. %s", path, message)
    raise RuntimeError(message)
  return ObjectID(imported_object)


def export_00t(
    object_id: ObjectID[Surface],
    path: str | pathlib.Path,
    unit: DistanceUnit=DistanceUnit.METRE):
  """Export a Surface to a Vulcan Triangulation (00t).

  Parameters
  ----------
  object_id
    The ID of the surface to export.
  path
    Where to save the 00t.
  unit
    Unit to use when exporting the file.

  Raises
  ------
  TypeError
    If the unit is not a DistanceUnit.
  RuntimeError
    If there was a problem exporting the file.

  Notes
  -----
  Changed in version 1.4 - This function no longer returns a value.
  Prior to 1.4, this would return True on success and raise an exception
  on failure (It could never return False).
  """
  log.info("Exporting Vulcan Triangulation (00t): %s", path)
  if not isinstance(path, pathlib.Path):
    path = pathlib.Path(path)

  if not isinstance(unit, DistanceUnit):
    raise TypeError(default_type_error_message("unit", unit, DistanceUnit))

  result = Vulcan().Write00tFile(object_id.handle,
                                 str(path).encode('utf-8'),
                                 unit.value)
  if not result:
    # This may be because the type of object can't be exported to a 00t or
    # because there was a problem trying to read the object or write to the
    # 00t.
    message = Vulcan().ErrorMessage().decode('utf-8')
    log.error("The 00t could not be exported: %s. %s", path, message)
    raise RuntimeError(message)


def import_bmf(
    path: str | pathlib.Path,
    unit: DistanceUnit=DistanceUnit.METRE
    ) -> ObjectID[BlockProperties | DataObject]:
  """Import a Maptek Block Model File (bmf) into the project.

  Parameters
  ----------
  path
    Path to file to import.
  unit
    Unit to use when importing the file.

  Returns
  -------
  ObjectID
    The ID of the imported object.

  Raises
  ------
  TypeError
    If path could not be converted to a pathlib.Path.
    If the unit is not an instance of DistanceUnit.
  FileNotFoundError
    If the file does not exist.
  RuntimeError
    If there is a problem importing the file.

  Notes
  -----
  The ObjectID returned by this function is type hinted as
  ObjectID[BlockProperties, DataObject] because all supported block models are
  expected to inherit from BlockProperties and DataObject. This means
  autocompletion should only suggest properties which are shared by all
  block models. The type hint may be incorrect if the bmf contains a block model
  not supported by the SDK.

  """
  log.info("Importing Vulcan Block Model (bmf): %s", path)

  if not isinstance(path, pathlib.Path):
    path = pathlib.Path(path)

  if not isinstance(unit, DistanceUnit):
    raise TypeError(default_type_error_message("unit", unit, DistanceUnit))

  if not path.is_file():
    raise FileNotFoundError(f"Could not find file: {path}")

  imported_object = Vulcan().ReadBmfFile(str(path).encode('utf-8'),
                                         unit.value)
  if imported_object.value == 0:
    message = Vulcan().ErrorMessage().decode('utf-8')
    log.error("A problem occurred when importing the BMF: %s", message)
    raise RuntimeError(message)
  return ObjectID(imported_object)


def export_bmf(
    object_id: ObjectID[BlockProperties | DataObject],
    path: str | pathlib.Path,
    unit: DistanceUnit=DistanceUnit.METRE):
  """Export a block model to a Maptek Block Model File (bmf).

  Parameters
  ----------
  object_id
    The ID of the block model to export as a bmf.
  path
    Where to save the bmf file.
  unit
    Unit to use when exporting the file.

  Returns
  -------
  bool
    True if the export was a success. This never returns false - if
    the import fails an exception will be raised.

  Raises
  ------
  TypeError
    If unit is not a DistanceUnit.
  RuntimeError
    If there was a problem exporting the file.

  Notes
  -----
  Changed in version 1.4 - This function no longer returns a value.
  Prior to 1.4, this would return True on success and raise an exception
  on failure (It could never return False).
  """
  log.info("Exporting Vulcan Block Model (bmf): %s", path)
  if not isinstance(path, pathlib.Path):
    path = pathlib.Path(path)

  if not isinstance(unit, DistanceUnit):
    raise TypeError(default_type_error_message("unit", unit, DistanceUnit))

  result = Vulcan().WriteBmfFile(object_id.handle,
                                 str(path).encode('utf-8'),
                                 unit.value)
  if not result:
    # This may be because the type of object can't be exported to a bmf or
    # because there was a problem trying to read the object or write to the
    # bmf.
    message = Vulcan().ErrorMessage().decode('utf-8')
    log.error("The BMF could not be exported to %s. %s", path, message)
    raise RuntimeError(message)


def import_maptekobj(path: str | pathlib.Path
    ) -> ObjectID[DataObject]:
  """Import a Maptek Object file (maptekobj) into the project.

  Parameters
  ----------
  path
    Path to file to import.

  Returns
  -------
  ObjectID
    The ID of the imported object.

  Raises
  ------
  FileNotFoundError
    If the file does not exist.
  RuntimeError
    If there is a problem importing the file.
  TypeError
    If path cannot be converted to a pathlib.Path object.

  """
  log.info("Importing Maptek Object file (maptekobj): %s", path)

  if not isinstance(path, pathlib.Path):
    path = pathlib.Path(path)

  if not path.is_file():
    raise FileNotFoundError(f"Could not find file: {path}")

  imported_object = DataEngine().ReadMaptekObjFile(
    str(path).encode('utf-8'))
  if imported_object.value == 0:
    last_error = DataEngine().ErrorMessage().decode("utf-8")
    log.error("A problem occurred (%s) when importing %s", last_error, path)
    raise RuntimeError(last_error)

  return ObjectID(imported_object)


def export_maptekobj(
    object_id: ObjectID[DataObject],
    path: str | pathlib.Path):
  """Export an object to a Maptek Object file (maptekobj).

  Unlike 00t and bmf any object (even containers) can be exported to a maptekobj
  file.

  Parameters
  ----------
  object_id
    The ID of the object to export.
  path
    Where to save the maptekobj file.

  Returns
  -------
  bool
    True if the export was a success. This never returns false - if
    the import fails an exception will be raised.

  Raises
  ------
  RuntimeError
    If there was a problem exporting the file.

  Notes
  -----
  Changed in version 1.4 - This function no longer returns a value.
  Prior to 1.4, this would return True on success and raise an exception
  on failure (It could never return False).
  """
  log.info("Exporting Maptek Object file (maptekobj): %s", path)
  if not isinstance(path, pathlib.Path):
    path = pathlib.Path(path)

  result = DataEngine().CreateMaptekObjFile(
    str(path).encode('utf-8'), object_id.handle)
  if not result:
    last_error = DataEngine().ErrorMessage().decode("utf-8")
    log.error("A problem occurred (%s) when importing %s", last_error, path)
    raise RuntimeError(last_error)
