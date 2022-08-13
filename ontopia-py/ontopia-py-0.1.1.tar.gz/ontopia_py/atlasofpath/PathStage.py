from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..ns import *
from ..route.Stage import Stage

if TYPE_CHECKING:
    from rdflib import Graph, Literal

    from ..acco.Accommodation import Accommodation
    from ..poi.PointOfInterest import PointOfInterest
    from .Restaurant import Restaurant
    from .Signposting import Signposting
    from .SupportService import SupportService


class PathStage(Stage):
    __type__ = PATHS["PathStage"]

    hasSignposting: List[Signposting] = None
    hasSupportService: List[SupportService] = None
    hasNearbyAccommodation: List[Accommodation] = None
    hasNearbyPointOfInterest: List[PointOfInterest] = None
    hasNearbyRestaurant: List[Restaurant] = None
    encountersPathStage: List[PathStage] = None
    stageNumber: List[Literal] = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.hasSignposting:
            for hasSignposting in self.hasSignposting:
                g.add(
                    (self.uriRef, PATHS["hasSignposting"], hasSignposting.uriRef))

        if self.hasSupportService:
            for hasSupportService in self.hasSupportService:
                g.add(
                    (self.uriRef, PATHS["hasSupportService"], hasSupportService.uriRef))

        if self.hasNearbyAccommodation:
            for hasNearbyAccommodation in self.hasNearbyAccommodation:
                g.add(
                    (self.uriRef, PATHS["hasNearbyAccommodation"], hasNearbyAccommodation.uriRef))

        if self.hasNearbyPointOfInterest:
            for hasNearbyPointOfInterest in self.hasNearbyPointOfInterest:
                g.add(
                    (self.uriRef, PATHS["hasNearbyPointOfInterest"], hasNearbyPointOfInterest.uriRef))

        if self.hasNearbyRestaurant:
            for hasNearbyRestaurant in self.hasNearbyRestaurant:
                g.add(
                    (self.uriRef, PATHS["hasNearbyRestaurant"], hasNearbyRestaurant.uriRef))

        if self.encountersPathStage:
            for encountersPathStage in self.encountersPathStage:
                g.add(
                    (self.uriRef, PATHS["encountersPathStage"], encountersPathStage.uriRef))

        if self.stageNumber:
            for stageNumber in self.stageNumber:
                g.add((self.uriRef, PATHS["stageNumber"], stageNumber))
