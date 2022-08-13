from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..ns import *
from ..poi.MultiplePointOfInterest import MultiplePointOfInterest
from .Accommodation import Accommodation

if TYPE_CHECKING:
    from rdflib import Graph


class AccommodationChain(Accommodation, MultiplePointOfInterest):
    __type__ = ACCO["AccommodationChain"]

    includesAccommodation: List[Accommodation] = None

    def _addProperties(self, g: Graph):
        MultiplePointOfInterest._addProperties(self, g)
        Accommodation._addProperties(self, g)

        if self.includesAccommodation:
            for includesAccommodation in self.includesAccommodation:
                g.add(
                    (self.uriRef, ACCO["includesAccommodation"], includesAccommodation.uriRef))
