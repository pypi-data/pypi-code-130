from __future__ import annotations

from typing import List, Optional, TypedDict

from atoti_core import CubeName, DimensionName, HierarchyName


class DiscoveryLevel(TypedDict):
    caption: str
    name: str
    type: str


class DiscoveryHierarchy(TypedDict):
    levels: List[DiscoveryLevel]
    name: HierarchyName
    slicing: bool
    caption: str


class DiscoveryDimension(TypedDict):
    hierarchies: List[DiscoveryHierarchy]
    name: DimensionName
    caption: str


class DiscoveryMeasure(TypedDict):
    name: str
    visible: bool
    folder: Optional[str]
    formatString: Optional[str]
    description: Optional[str]
    caption: str


class DiscoveryCube(TypedDict):
    dimensions: List[DiscoveryDimension]
    measures: List[DiscoveryMeasure]
    name: CubeName


class DiscoveryCatalog(TypedDict):
    cubes: List[DiscoveryCube]


class Discovery(TypedDict):
    catalogs: List[DiscoveryCatalog]
