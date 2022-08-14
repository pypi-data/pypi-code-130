from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..ns import *
from ..poi.PointOfInterest import PointOfInterest

if TYPE_CHECKING:
    from rdflib import Graph, Literal

    from ..accesscondition.AccessCondition import AccessCondition
    from ..pot.Offer import Offer
    from ..sm.OnlineContactPoint import OnlineContactPoint
    from ..sm.Review import Review
    from .CarParkTypology import CarParkTypology


class CarPark(PointOfInterest):
    __type__ = PARK["CarPark"]

    hasOffer: List[Offer] = None
    hasOnlineContactPoint: List[OnlineContactPoint] = None
    hasReview: List[Review] = None
    hasCarParkTypology: List[CarParkTypology] = None
    hasAccessCondition: List[AccessCondition] = None
    carParkName: List[Literal] = None
    carParkDescription: List[Literal] = None
    numSpacesForDisabled: Literal = None
    numPayingParkingSpaces: Literal = None
    numAvailableParkingSpaces: Literal = None
    numSoldCarParkSpaces: Literal = None
    totalNumCarParkSpaces: Literal = None
    carParkID: Literal = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.hasOffer:
            for hasOffer in self.hasOffer:
                g.add((self.uriRef, POT["hasOffer"], hasOffer.uriRef))

        if self.hasOnlineContactPoint:
            for hasOnlineContactPoint in self.hasOnlineContactPoint:
                g.add(
                    (self.uriRef, SM["hasOnlineContactPoint"], hasOnlineContactPoint.uriRef))

        if self.hasReview:
            for hasReview in self.hasReview:
                g.add((self.uriRef, SM["hasReview"], hasReview.uriRef))

        if self.hasCarParkTypology:
            for hasCarParkTypology in self.hasCarParkTypology:
                g.add(
                    (self.uriRef, PARK["hasCarParkTypology"], hasCarParkTypology.uriRef))

        if self.hasAccessCondition:
            for hasAccessCondition in self.hasAccessCondition:
                g.add(
                    (self.uriRef, ACOND["hasAccessCondition"], hasAccessCondition.uriRef))

        if self.carParkName:
            for carParkName in self.carParkName:
                g.add((self.uriRef, PARK["carParkName"], carParkName))

        if self.carParkDescription:
            for carParkDescription in self.carParkDescription:
                g.add(
                    (self.uriRef, PARK["carParkDescription"], carParkDescription))

        if self.numSpacesForDisabled:
            g.add(
                (self.uriRef, PARK["numSpacesForDisabled"], self.numSpacesForDisabled))

        if self.numPayingParkingSpaces:
            g.add(
                (self.uriRef, PARK["numPayingParkingSpaces"], self.numPayingParkingSpaces))

        if self.numAvailableParkingSpaces:
            g.add(
                (self.uriRef, PARK["numAvailableParkingSpaces"], self.numAvailableParkingSpaces))

        if self.numSoldCarParkSpaces:
            g.add(
                (self.uriRef, PARK["numSoldCarParkSpaces"], self.numSoldCarParkSpaces))

        if self.totalNumCarParkSpaces:
            g.add(
                (self.uriRef, PARK["totalNumCarParkSpaces"], self.totalNumCarParkSpaces))

        if self.carParkID:
            g.add((self.uriRef, PARK["carParkID"], self.carParkID))
