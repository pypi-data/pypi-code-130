from __future__ import annotations

from typing import TYPE_CHECKING

from ontopia_py.iot.RoadSegment import RoadSegment

from ..ns import *

if TYPE_CHECKING:
    from ontopia_py.clv.StreetToponym import StreetToponym
    from rdflib import Graph


class RoadSegment(RoadSegment):
    __type__ = ONTOIM["RoadSegment"]

    hasStreetToponym: StreetToponym = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.hasStreetToponym:
            g.add(
                (self.uriRef, CLV["hasStreetToponym"], self.hasStreetToponym.uriRef))
