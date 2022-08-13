from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..clv.Feature import Feature
from ..ns import *
from ..poi.PointOfInterest import PointOfInterest

if TYPE_CHECKING:
    from rdflib import Graph, Literal

    from ..clv.Address import Address
    from ..clv.Feature import Feature
    from ..sm.OnlineContactPoint import OnlineContactPoint
    from .CulturalEvent import CulturalEvent
    from .CulturalInstituteOrSite import CulturalInstituteOrSite
    from .SiteDescription import SiteDescription


class Site(Feature, PointOfInterest):
    __type__ = CIS["Site"]

    isSiteOf: List[CulturalInstituteOrSite] = None
    hasSiteDescription: List[SiteDescription] = None
    hostsCulturalEvent: List[CulturalEvent] = None
    siteAddress: List[CulturalInstituteOrSite] = None
    isSiteOf: List[Address] = None
    hasSpatialCoverage: List[Feature] = None
    hasOnlineContactPoint: List[OnlineContactPoint] = None
    description: List[Literal] = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.isSiteOf:
            for isSiteOf in self.isSiteOf:
                g.add((self.uriRef, CIS["isSiteOf"], isSiteOf.uriRef))

        if self.hasSiteDescription:
            for hasSiteDescription in self.hasSiteDescription:
                g.add(
                    (self.uriRef, CIS["hasSiteDescription"], hasSiteDescription.uriRef))

        if self.hostsCulturalEvent:
            for hostsCulturalEvent in self.hostsCulturalEvent:
                g.add(
                    (self.uriRef, CIS["hostsCulturalEvent"], hostsCulturalEvent.uriRef))

        if self.siteAddress:
            for siteAddress in self.siteAddress:
                g.add((self.uriRef, CIS["siteAddress"], siteAddress.uriRef))

        if self.isSiteOf:
            for isSiteOf in self.isSiteOf:
                g.add((self.uriRef, CIS["isSiteOf"], isSiteOf.uriRef))

        if self.hasSpatialCoverage:
            for hasSpatialCoverage in self.hasSpatialCoverage:
                g.add(
                    (self.uriRef, CLV["hasSpatialCoverage"], hasSpatialCoverage.uriRef))

        if self.hasOnlineContactPoint:
            for hasOnlineContactPoint in self.hasOnlineContactPoint:
                g.add(
                    (self.uriRef, SM["hasOnlineContactPoint"], hasOnlineContactPoint.uriRef))

        if self.description:
            for description in self.description:
                g.add((self.uriRef, L0["description"], description))
