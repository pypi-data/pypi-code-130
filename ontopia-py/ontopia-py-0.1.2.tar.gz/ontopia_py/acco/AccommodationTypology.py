from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..l0.Topic import Topic
from ..ns import *

if TYPE_CHECKING:
    from rdflib import Graph

    from .Accommodation import Accommodation


class AccommodationTypology(Topic):
    __type__ = ACCO["AccommodationTypology"]

    isAccommodationTypologyOf: List[Accommodation] = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.isAccommodationTypologyOf:
            for isAccommodationTypologyOf in self.isAccommodationTypologyOf:
                g.add(
                    (self.uriRef, ACCO["isAccommodationTypologyOf"], isAccommodationTypologyOf.uriRef))
