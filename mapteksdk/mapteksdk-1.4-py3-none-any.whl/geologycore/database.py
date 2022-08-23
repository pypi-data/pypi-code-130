"""Drillhole database data types."""
###############################################################################
#
# (C) Copyright 2022, Maptek Pty Ltd. All rights reserved.
#
###############################################################################
from __future__ import annotations

import json

from .drillholes import Drillhole
from .errors import DatabaseLoadError, DuplicateTableTypeError
from .internal.constants import DATABASE_CONSTANTS
from .internal.tables_mixin import TablesMixin
from .tables import (DrillholeTableType, BaseTableInformation,
                     CollarTableInformation, AssayTableInformation,
                     SurveyTableInformation, GeologyTableInformation,
                     QualityTableInformation, DownholeTableInformation,
                     CustomTableInformation)
from ..capi.drillholemodel import DrillholeModel
from ..capi.util import CApiDllLoadFailureError
from ..data.containers import VisualContainer
from ..data.errors import ReadOnlyError, ObjectNotSupportedError
from ..data.objectid import ObjectID
from ..internal.lock import LockType
from ..internal.util import default_type_error_message

class DrillholeDatabase(VisualContainer, TablesMixin):
  """A container which contains Drillhole objects.

  A DrillholeDatabase object is backed by a database. This database may
  be a Vulcan Isis database, a set of CSV files or an internal database.

  New databases created through this interface are always backed by an internal
  database. Upon creation, the new database contains a single
  table (A collar table containing a northing field and an easting field) and
  no drillholes.

  Raises
  ------
  EmptyTableError
    If any table in the database contains no fields.
  DuplicateFieldTypeError
    If any table contains multiple fields of a type which does not support
    duplicates.
  MissingRequiredFieldsError
    If any table does not contain all of its required fields.

  Examples
  --------
  Creating a new drillhole database containing a single drillhole.
  This is a simple example which only uses two tables (A collar table and a
  geology table).

  >>> from mapteksdk.project import Project
  >>> from mapteksdk.data import StringColourMap
  >>> from mapteksdk.geologycore import (
  ...   DrillholeDatabase, DrillholeTableType, DrillholeFieldType)
  >>> with Project() as project:
  ...   # The colour map to use to colour the drillhole.
  ...   with project.new("drillholes/geology_rock_type", StringColourMap
  ...       ) as colour_map:
  ...     colour_map.legend = ["DIRT", "ROCK", "UNOBTAINIUM"]
  ...     colour_map.colours = [
  ...       [165, 42, 42, 255],
  ...       [100, 100, 100, 255],
  ...       [255, 215, 0, 255]
  ...     ]
  ...   with project.new("drillholes/new_database", DrillholeDatabase
  ...       ) as database:
  ...     # The newly created database automatically contains a collar table,
  ...     # so the creator does not need to create one.
  ...     # The collar table only initially contains a northing and an easting
  ...     # field. To be able to more accurately place the drillhole, add an
  ...     # elevation field.
  ...     collar_table = database.collar_table
  ...     collar_table.add_field(
  ...       "ELEVATION",
  ...       float,
  ...       "Elevation of the drillhole",
  ...       field_type=DrillholeFieldType.ELEVATION
  ...     )
  ...     database.add_table("GEOLOGY", DrillholeTableType.GEOLOGY)
  ...     geology_table = database.geology_table
  ...     # The newly created geology table automatically contains to depth
  ...     # and from depth fields so the creator does not need to create them.
  ...     geology_table.add_field(
  ...       "ROCK_TYPE",
  ...       str,
  ...       "The type of rock in the interval",
  ...       field_type=DrillholeFieldType.ROCK_TYPE)
  ...     # Add a new drillhole to the database.
  ...     drillhole_id= database.new_drillhole("D-1")
  ...   with project.edit(drillhole_id) as drillhole:
  ...     # Set the collar point.
  ...     drillhole.raw_collar = (-0.7, 1.6, -15.6)
  ...     # Populate the geology table.
  ...     geology_table = drillhole.geology_table
  ...     geology_table.add_rows(3)
  ...     geology_table.from_depth.values = [0, 12.3, 25.1]
  ...     geology_table.to_depth.values = [12.3, 25.1, 34.4]
  ...     geology_table.rock_type.values = [
  ...       "DIRT",
  ...       "ROCK",
  ...       "UNOBTAINIUM"]
  ...     drillhole.set_visualisation(geology_table.rock_type,
  ...                                 colour_map)
  """
  def __init__(
      self, object_id: ObjectID | None=None, lock_type: LockType=LockType.READ):
    is_new = not object_id
    if is_new:
      object_id = self._create_object()

    self._initialise_table_variables()

    super().__init__(object_id, lock_type)

    self.__refresh_drillholes: bool = False
    """If the drillholes should be refreshed when this object is saved."""

    if is_new:
      # Add a collar table to the database. This is the minimum amount of
      # tables required for the new database to be 'valid'.
      self.add_table(DrillholeTableType.COLLAR.name, DrillholeTableType.COLLAR)

  def _create_object(self) -> ObjectID[DrillholeDatabase]:
    try:
      return ObjectID(DrillholeModel().NewInternalDatabase())
    except CApiDllLoadFailureError as error:
      raise ObjectNotSupportedError(
        DrillholeDatabase) from error

  def _to_json_dictionary(self) -> dict:
    """Return a dictionary representing this object.

    This dictionary is formatted to be ready to be serialised to JSON.
    """
    # pylint: disable=protected-access
    database_information = {
      DATABASE_CONSTANTS.VERSION : 1,
      DATABASE_CONSTANTS.TABLES : [
        table._to_json_dictionary() for table in self.tables
      ]
    }

    return database_information

  def save(self):
    # Check all the tables are valid if they are cached.
    if self._tables is not None:
      for table in self.tables:
        # pylint: disable=protected-access
        table._raise_if_invalid()
      DrillholeModel().DatabaseFromJson(
        self._lock.lock, json.dumps(self._to_json_dictionary()))
      super().save()
    if self.__refresh_drillholes:
      DrillholeModel().DatabaseRefreshDrillholes(self._lock.lock)
      self.__refresh_drillholes = False

  @property
  def id(self) -> ObjectID[DrillholeDatabase]:
    return super().id

  @classmethod
  def static_type(cls):
    return DrillholeModel().DatabaseType()

  def close(self):
    super().close()
    self._unlink()

  def new_drillhole(self, drillhole_id: str) -> ObjectID[Drillhole]:
    """Create a new drillhole and add it to the database.

    The drillhole should be opened using the ObjectID returned by this
    function. The drillhole is inserted into the drillhole database
    container with drillhole_id as its name.

    Opening the new drillhole for reading or editing before closing
    the drillhole database will raise an OrphanDrillholeError.

    Parameters
    ----------
    drillhole_id
      Unique id for the new drillhole.

    Raises
    ------
    ValueError
      If there is already a drillhole with the specified ID or if
      the drillhole could not be created.
    TypeError
      If drillhole_id is not a str.
    ReadOnlyError
      If this object is open for read-only.

    Notes
    -----
    If there is an object at the path where the drillhole will be inserted,
    that object will be silently orphaned and the path will now refer
    to the new drillhole.
    """
    if self.lock_type is not LockType.READWRITE:
      raise ReadOnlyError("Cannot add a new drillhole to read-only database.")
    if not isinstance(drillhole_id, str):
      raise TypeError(
        default_type_error_message("drillhole_id", drillhole_id, str))
    self.save()
    drillhole_handle = DrillholeModel().NewDrillhole(
      self._lock.lock, drillhole_id)
    return ObjectID(drillhole_handle)

  def add_table(
      self,
      table_name: str,
      table_type: DrillholeTableType=DrillholeTableType.OTHER):
    """Add a new table to the database.

    The newly created table will contain any fields required by the specified
    table type (For example, to and from depth fields for assay tables).

    Parameters
    ----------
    table_name
      The name for the new table.
    table_type
      The type of the new table. This is DrillholeTableType.OTHER by default.

    Raises
    ------
    ValueError
      If table_type is DrillholeTableType.UNKNOWN.
    TypeError
      If table_type is not part of the DrillholeTableType enum.
    DuplicateTableTypeError
      If attempting to add a second collar or survey table to a database.

    Notes
    -----
    When creating a table which supports TO_DEPTH or FROM_DEPTH fields,
    this function will automatically add both TO_DEPTH and FROM_DEPTH fields to
    the table. Though it is valid for a table to contain only a
    TO_DEPTH field or only a FROM_DEPTH field, it is not possible to create
    such a table through this function.
    """
    if self.lock_type is not LockType.READWRITE:
      raise ReadOnlyError("Cannot add a new table to read-only database.")

    # Ensure the existing tables are loaded.
    self._load_tables()

    if table_type is DrillholeTableType.UNKNOWN:
      raise ValueError(
        f"Creating tables of '{table_type}' is not supported. "
        f"Use '{DrillholeTableType.OTHER}' for non built-in tables.")

    try:
      table_class = self._table_type_to_class()[table_type]
    except KeyError as error:
      raise TypeError(f"Unsupported table type: '{table_type}'.") from error

    # Raise an error if the table type does not support duplicates.
    if (table_type.must_be_unique()
        and len(self.tables_by_type(table_type)) != 0):
      raise DuplicateTableTypeError(table_type)

    table_information = {
      DATABASE_CONSTANTS.NAME : table_name
    }
    table = table_class(table_information)

    # Add the table in Python. This will ensure it is available via
    # fields_by_type, field_by_name.
    self._add_table(table)

    # Add the required fields to the table. This ensures tables always
    # contain their required fields.
    # pylint: disable=protected-access
    table._add_required_fields()

  def refresh_holes(self):
    """Forces the visualisation of the drillholes to be refreshed.

    The refresh occurs when the database is saved. This should be called when
    an edit to the database design will change how existing drillholes are
    visualised, typically due to field types being changed.

    Warnings
    --------
    This operation can be quite slow on databases with a large number
    of drillholes.
    """
    self.__refresh_drillholes = True

  @property
  def assay_table(self) -> AssayTableInformation:
    return super().assay_table

  @property
  def collar_table(self) -> CollarTableInformation:
    return super().collar_table

  @property
  def survey_table(self) -> SurveyTableInformation:
    return super().survey_table

  @property
  def geology_table(self) -> GeologyTableInformation:
    return super().geology_table

  @property
  def downhole_table(self) -> DownholeTableInformation:
    return super().downhole_table

  @property
  def quality_table(self) -> QualityTableInformation:
    return super().quality_table

  @property
  def tables(self) -> list[BaseTableInformation]:
    return super().tables

  # pylint: disable=useless-super-delegation
  # pylint incorrectly identifies the following as "useless
  # super delegation" because they only change the type hint.
  # See https://github.com/PyCQA/pylint/issues/5822 for progress.
  def tables_by_type(self, table_type: DrillholeTableType
      ) ->  list[BaseTableInformation]:
    return super().tables_by_type(table_type)

  def table_by_name(self, name: str) -> BaseTableInformation:
    return super().table_by_name(name)

  def _table_by_type(
      self, table_type: DrillholeTableType, error_multiple_tables: bool=False
      ) -> BaseTableInformation:
    return super()._table_by_type(table_type, error_multiple_tables)
  # pylint: enable=useless-super-delegation

  def _load_database_information(self) -> str:
    if self._lock.is_closed:
      raise ValueError("Cannot access a closed object.")
    try:
      return DrillholeModel().GetDatabaseInformation(self.id.handle)
    except Exception as error:
      raise DatabaseLoadError(
        f"Failed to read the database for '{self.id.name}'. "
        "It may not be inside a DrillholeDatabase or the drillhole "
        "may have been deleted from the database."
      ) from error

  @classmethod
  def _table_type_to_class(cls):
    return {
      DrillholeTableType.ASSAY: AssayTableInformation,
      DrillholeTableType.COLLAR : CollarTableInformation,
      DrillholeTableType.DOWNHOLE : DownholeTableInformation,
      DrillholeTableType.GEOLOGY : GeologyTableInformation,
      DrillholeTableType.QUALITY : QualityTableInformation,
      DrillholeTableType.SURVEY : SurveyTableInformation,
      DrillholeTableType.OTHER : CustomTableInformation
    }

  @classmethod
  def _default_table_type(cls):
    return CustomTableInformation
