from __future__ import annotations

from typing import TYPE_CHECKING, List

from ontopia_py.poi.PointOfInterest import PointOfInterest

from ..ns import *

if TYPE_CHECKING:
    from rdflib import Graph, Literal

    from .RoadSignalType import RoadSignalType


class RoadSignal(PointOfInterest):
    __type__ = ONTOIM["RoadSignal"]

    hasRoadSignalType: RoadSignalType = None
    signalValue: List[Literal] = None
    installationDate: Literal = None
    removalDate: Literal = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.hasRoadSignalType:
            g.add(
                (self.uriRef, ONTOIM["hasRoadSignalType"], self.hasRoadSignalType.uriRef))

        if self.signalValue:
            for signalValue in self.signalValue:
                g.add((self.uriRef, ONTOIM["signalValue"], signalValue))

        if self.installationDate:
            g.add(
                (self.uriRef, ONTOIM["installationDate"], self.installationDate))

        if self.removalDate:
            g.add((self.uriRef, ONTOIM["removalDate"], self.removalDate))
