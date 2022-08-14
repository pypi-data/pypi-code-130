from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..l0.Entity import Entity
from ..ns import *

if TYPE_CHECKING:
    from rdflib import Graph, Literal

    from ..clv.Address import Address
    from ..clv.Geometry import Geometry
    from ..sm.Image import Image
    from ..ti.TimeInterval import TimeInterval
    from .MultiplePointOfInterest import MultiplePointOfInterest
    from .POINameInTime import POINameInTime
    from .PointOfInterestCategory import PointOfInterestCategory
    from .POIState import POIState


class PointOfInterest(Entity):
    __type__ = POI["PointOfInterest"]

    hasPOICategory: List[PointOfInterestCategory] = []
    hasAddress: List[Address] = []
    hasPOINameInITime: List[POINameInTime] = None
    hasImage: List[Image] = None
    atTime: List[TimeInterval] = None
    hasGeometry: Geometry = None
    hasPOIState: POIState = None
    isIncludedInPOI: MultiplePointOfInterest = None
    POIofficialName: List[Literal] = None
    POIdescription: List[Literal] = None
    POIID: Literal = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.hasPOICategory:
            for hasPOICategory in self.hasPOICategory:
                g.add(
                    (self.uriRef, POI["hasPOICategory"], hasPOICategory.uriRef))

        if self.hasAddress:
            for hasAddress in self.hasAddress:
                g.add((self.uriRef, CLV["hasAddress"], hasAddress.uriRef))

        if self.hasPOINameInITime:
            for hasPOINameInITime in self.hasPOINameInITime:
                g.add(
                    (self.uriRef, POI["hasPOINameInITime"], hasPOINameInITime.uriRef))

        if self.hasImage:
            for hasImage in self.hasImage:
                g.add(
                    (self.uriRef, SM["hasImage"], hasImage.uriRef))

        if self.atTime:
            for atTime in self.atTime:
                g.add(
                    (self.uriRef, TI["atTime"], atTime.uriRef))

        if self.hasGeometry:
            g.add((self.uriRef, CLV["hasGeometry"], self.hasGeometry.uriRef))

        if self.hasPOIState:
            g.add((self.uriRef, CLV["hasPOIState"], self.hasPOIState.uriRef))

        if self.isIncludedInPOI:
            g.add((self.uriRef, CLV["isIncludedInPOI"],
                  self.isIncludedInPOI.uriRef))

        if self.POIofficialName:
            for POIofficialName in self.POIofficialName:
                g.add((self.uriRef, POI["POIofficialName"], POIofficialName))

        if self.POIdescription:
            for POIdescription in self.POIdescription:
                g.add((self.uriRef, POI["POIdescription"], POIdescription))

        if self.POIID:
            g.add((self.uriRef, POI["POIID"], self.POIID))
