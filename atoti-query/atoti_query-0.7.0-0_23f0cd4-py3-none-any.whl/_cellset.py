from __future__ import annotations

from typing import Optional, Sequence, TypedDict, Union

from atoti_core import CubeName, DimensionName, HierarchyName

MeasureValue = Optional[Union[float, int, str]]
MemberIdentifier = str


class CellsetHierarchy(TypedDict):
    dimension: DimensionName
    hierarchy: HierarchyName


class CellsetMember(TypedDict):
    captionPath: Sequence[str]
    namePath: Sequence[MemberIdentifier]


class CellsetAxis(TypedDict):
    id: int
    hierarchies: Sequence[CellsetHierarchy]
    positions: Sequence[Sequence[CellsetMember]]


class CellsetCellProperties(TypedDict):
    BACK_COLOR: Optional[Union[int, str]]
    FONT_FLAGS: Optional[int]
    FONT_NAME: Optional[str]
    FONT_SIZE: Optional[int]
    FORE_COLOR: Optional[Union[int, str]]


class CellsetCell(TypedDict):
    formattedValue: str
    ordinal: int
    properties: CellsetCellProperties
    value: MeasureValue


class CellsetDefaultMember(TypedDict):
    captionPath: Sequence[str]
    dimension: DimensionName
    hierarchy: HierarchyName
    path: Sequence[MemberIdentifier]


class Cellset(TypedDict):
    axes: Sequence[CellsetAxis]
    cells: Sequence[CellsetCell]
    cube: CubeName
    defaultMembers: Sequence[CellsetDefaultMember]
