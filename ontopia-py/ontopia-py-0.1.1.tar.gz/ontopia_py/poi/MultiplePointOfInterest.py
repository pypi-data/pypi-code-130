from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..ns import *
from .PointOfInterest import PointOfInterest

if TYPE_CHECKING:
    from rdflib import Graph


class MultiplePointOfInterest(PointOfInterest):
    __type__ = POI["MultiplePointOfInterest"]

    includesPOI: List[PointOfInterest] = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.includesPOI:
            for includesPOI in self.includesPOI:
                g.add((self.uriRef, POI["includesPOI"], includesPOI.uriRef))
