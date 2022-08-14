from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..ns import *
from .SpatialObject import SpatialObject

if TYPE_CHECKING:
    from rdflib import Graph, Literal

    from ..Thing import Thing
    from .GeometryType import GeometryType


class Geometry(SpatialObject):
    __type__ = CLV["Geometry"]

    hasGeometryType: GeometryType = None
    lat: Literal = None
    long: Literal = None
    alt: Literal = None
    coordinate: Literal = None
    coordinateSystem: Literal = None
    serialization: Literal = None
    isGeometryFor: List[Thing] = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.hasGeometryType:
            g.add((self.uriRef, CLV["hasGeometryType"],
                  self.hasGeometryType.uriRef))

        if self.lat:
            g.add((self.uriRef, CLV["lat"], self.lat))

        if self.long:
            g.add((self.uriRef, CLV["long"], self.long))

        if self.alt:
            g.add((self.uriRef, CLV["alt"], self.alt))

        if self.coordinate:
            g.add((self.uriRef, CLV["coordinate"], self.coordinate))

        if self.coordinateSystem:
            g.add((self.uriRef, CLV["coordinateSystem"],
                  self.coordinateSystem))

        if self.serialization:
            g.add((self.uriRef, CLV["serialization"], self.serialization))

        if self.isGeometryFor:
            for isGeometryFor in self.isGeometryFor:
                g.add(
                    (self.uriRef, CLV["isGeometryFor"], isGeometryFor.uriRef))
