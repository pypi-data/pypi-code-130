from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..ns import *
from .OSDFeature import OSDFeature

if TYPE_CHECKING:
    from rdflib import Graph, Literal

    from ..pot.Offer import Offer
    from .Accommodation import Accommodation
    from .OfferedServiceDescription import OfferedServiceDescription


class AccommodationRoom(OSDFeature):
    __type__ = ACCO["AccommodationRoom"]

    hasOfferedServiceDescription: List[OfferedServiceDescription] = None
    hasOffer: List[Offer] = None
    isAccommodationRoomOf: Accommodation = None
    roomName: Literal = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.hasOfferedServiceDescription:
            for hasOfferedServiceDescription in self.hasOfferedServiceDescription:
                g.add(
                    (self.uriRef, ACCO["hasOfferedServiceDescription"], hasOfferedServiceDescription.uriRef))

        if self.hasOffer:
            for hasOffer in self.hasOffer:
                g.add((self.uriRef, POT["hasOffer"], hasOffer.uriRef))

        if self.isAccommodationRoomOf:
            g.add((self.uriRef, ACCO["isAccommodationRoomOf"],
                  self.isAccommodationRoomOf.uriRef))

        if self.roomName:
            g.add((self.uriRef, ACCO["roomName"], self.roomName))
