from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..l0.Characteristic import Characteristic
from ..ns import *

if TYPE_CHECKING:
    from rdflib import Graph, Literal

    from .Accommodation import Accommodation


class AccommodationStarRating(Characteristic):
    __type__ = ACCO["AccommodationStarRating"]

    isAccommodationClassificationOf: List[Accommodation] = None
    accoStarRatingLabel: List[Literal] = None
    accoStarRatingID: List[Literal] = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.isAccommodationClassificationOf:
            for isAccommodationClassificationOf in self.isAccommodationClassificationOf:
                g.add((self.uriRef, ACCO["isAccommodationClassificationOf"],
                      isAccommodationClassificationOf.uriRef))

        if self.accoStarRatingLabel:
            for accoStarRatingLabel in self.accoStarRatingLabel:
                g.add(
                    (self.uriRef, ACCO["accoStarRatingLabel"], accoStarRatingLabel))

        if self.accoStarRatingID:
            for accoStarRatingID in self.accoStarRatingID:
                g.add(
                    (self.uriRef, ACCO["accoStarRatingID"], accoStarRatingID))
