from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..ns import *
from ..poi.PointOfInterest import PointOfInterest

if TYPE_CHECKING:
    from rdflib import Graph, Literal

    from ..l0.Agent import Agent
    from ..pot.Offer import Offer
    from ..sm.OnlineContactPoint import OnlineContactPoint
    from ..sm.Review import Review
    from .AccommodationChain import AccommodationChain
    from .AccommodationRoom import AccommodationRoom
    from .AccommodationStarRating import AccommodationStarRating
    from .AccommodationTypology import AccommodationTypology
    from .OfferedServiceDescription import OfferedServiceDescription


class Accommodation(PointOfInterest):
    __type__ = ACCO["Accommodation"]

    accommodationCode: List[Literal] = None
    hasAccommodationTypology: List[AccommodationTypology] = None
    hasAccommodationRoom: List[AccommodationRoom] = None
    hasOfferedServiceDescription: List[OfferedServiceDescription] = None
    isIncludedInAccommodation: List[AccommodationChain] = None
    hasOffer: List[Offer] = None
    hasReview: List[Review] = None
    hasAccommodationClassification: AccommodationStarRating = None
    hasAccommodationOwner: Agent = None
    hasOnlineContactPoint: OnlineContactPoint = None
    totalBed: Literal = None
    totalRoom: Literal = None
    totalToilet: Literal = None
    checkIn: Literal = None
    checkOut: Literal = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.accommodationCode:
            for accommodationCode in self.accommodationCode:
                g.add(
                    (self.uriRef, ACCO["accommodationCode"], accommodationCode))

        if self.hasAccommodationTypology:
            for hasAccommodationTypology in self.hasAccommodationTypology:
                g.add(
                    (self.uriRef, ACCO["hasAccommodationTypology"], hasAccommodationTypology.uriRef))

        if self.hasAccommodationRoom:
            for hasAccommodationRoom in self.hasAccommodationRoom:
                g.add(
                    (self.uriRef, ACCO["hasAccommodationRoom"], hasAccommodationRoom.uriRef))

        if self.hasOfferedServiceDescription:
            for hasOfferedServiceDescription in self.hasOfferedServiceDescription:
                g.add(
                    (self.uriRef, ACCO["hasOfferedServiceDescription"], hasOfferedServiceDescription.uriRef))

        if self.isIncludedInAccommodation:
            for isIncludedInAccommodation in self.isIncludedInAccommodation:
                g.add(
                    (self.uriRef, ACCO["isIncludedInAccommodation"], isIncludedInAccommodation.uriRef))

        if self.hasOffer:
            for hasOffer in self.hasOffer:
                g.add((self.uriRef, POT["hasOffer"], hasOffer.uriRef))

        if self.hasReview:
            for hasReview in self.hasReview:
                g.add((self.uriRef, SM["hasReview"], hasReview.uriRef))

        if self.hasAccommodationClassification:
            g.add((self.uriRef, ACCO["hasAccommodationClassification"],
                  self.hasAccommodationClassification.uriRef))

        if self.hasAccommodationOwner:
            g.add((self.uriRef, ACCO["hasAccommodationOwner"],
                  self.hasAccommodationOwner.uriRef))

        if self.hasOnlineContactPoint:
            g.add((self.uriRef, SM["hasOnlineContactPoint"],
                  self.hasOnlineContactPoint.uriRef))

        if self.totalBed:
            g.add((self.uriRef, ACCO["totalBed"], self.totalBed))

        if self.totalRoom:
            g.add((self.uriRef, ACCO["totalRoom"], self.totalRoom))

        if self.totalToilet:
            g.add((self.uriRef, ACCO["totalToilet"], self.totalToilet))

        if self.checkIn:
            g.add((self.uriRef, ACCO["checkIn"], self.checkIn))

        if self.checkOut:
            g.add((self.uriRef, ACCO["checkOut"], self.checkOut))
