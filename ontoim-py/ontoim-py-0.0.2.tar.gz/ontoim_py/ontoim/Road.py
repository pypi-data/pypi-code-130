from __future__ import annotations

from typing import TYPE_CHECKING, List

from ontopia_py.l0.Location import Location

from ..ns import *

if TYPE_CHECKING:
    from ontopia_py.clv.Address import Address
    from rdflib import Graph, Literal

    from .PavementType import PavementType
    from .RoadbedStatus import RoadbedStatus
    from .RoadCategory import RoadCategory
    from .RoadContext import RoadContext
    from .RoadSignalPresence import RoadSignalPresence
    from .RoadType import RoadType


class Road(Location):
    __type__ = ONTOIM["Road"]

    hasAddress: Address = None
    hasPavementType: PavementType = None
    hasRoadCategory: RoadCategory = None
    hasRoadContext: RoadContext = None
    hasRoadSignalPresence: RoadSignalPresence = None
    hasRoadType: RoadType = None
    hasRoadbedStatus: RoadbedStatus = None
    roadName: List[Literal] = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.hasAddress:
            g.add((self.uriRef, ONTOIM["hasAddress"], self.hasAddress.uriRef))

        if self.hasPavementType:
            g.add(
                (self.uriRef, ONTOIM["hasPavementType"], self.hasPavementType.uriRef))

        if self.hasRoadCategory:
            g.add(
                (self.uriRef, ONTOIM["hasRoadCategory"], self.hasRoadCategory.uriRef))

        if self.hasRoadContext:
            g.add(
                (self.uriRef, ONTOIM["hasRoadContext"], self.hasRoadContext.uriRef))

        if self.hasRoadSignalPresence:
            g.add(
                (self.uriRef, ONTOIM["hasRoadSignalPresence"], self.hasRoadSignalPresence.uriRef))

        if self.hasRoadType:
            g.add((self.uriRef, ONTOIM["hasRoadType"],
                  self.hasRoadType.uriRef))

        if self.hasRoadbedStatus:
            g.add(
                (self.uriRef, ONTOIM["hasRoadbedStatus"], self.hasRoadbedStatus.uriRef))

        if self.roadName:
            for roadName in self.roadName:
                g.add(
                    (self.uriRef, ONTOIM["roadName"], roadName))
