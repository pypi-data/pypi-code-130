from typing import Tuple, Union

ColumnKey = Tuple[str, str]

CubeName = str

DimensionName = str

HierarchyName = str
HierarchyCoordinates = Tuple[DimensionName, HierarchyName]

HierarchyKey = Union[HierarchyName, HierarchyCoordinates]

LevelName = str
LevelCoordinates = Tuple[DimensionName, HierarchyName, LevelName]

LevelKey = Union[LevelName, Tuple[HierarchyName, LevelName], LevelCoordinates]
