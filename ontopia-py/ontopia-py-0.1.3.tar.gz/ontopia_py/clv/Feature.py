from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..ns import *
from .SpatialObject import SpatialObject

if TYPE_CHECKING:
    from rdflib import Graph, Literal

    from ..Thing import Thing
    from .Geometry import Geometry


class Feature(SpatialObject):
    __type__ = CLV["Feature"]

    hasGeometry: List[Geometry] = None
    modified: Literal = None
    isSpatialCoverageOf: List[Thing] = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.hasGeometry:
            for hasGeometry in self.hasGeometry:
                g.add((self.uriRef, CLV["hasGeometry"], hasGeometry.uriRef))

        if self.modified:
            g.add((self.uriRef, TI["modified"], self.modified))

        if self.isSpatialCoverageOf:
            for isSpatialCoverageOf in self.isSpatialCoverageOf:
                g.add(
                    (self.uriRef, CLV["isSpatialCoverageOf"], isSpatialCoverageOf.uriRef))
