from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..ns import *
from .Event import Event

if TYPE_CHECKING:
    from rdflib import Graph, Literal

    from ..accesscondition.AccessCondition import AccessCondition
    from ..poi.PointOfInterest import PointOfInterest
    from ..pot.Offer import Offer
    from ..ro.TimeIndexedRole import TimeIndexedRole
    from ..sm.Image import Image
    from ..sm.OnlineContactPoint import OnlineContactPoint
    from ..sm.Review import Review
    from .Audience import Audience
    from .Playbill import Playbill
    from .PublicEventTypology import PublicEventTypology


class PublicEvent(Event):
    __type__ = COV["PublicEvent"]

    hasPublicEventTypology: List[PublicEventTypology] = None
    takesPlaceIn: List[PointOfInterest] = None
    hasRiT: List[TimeIndexedRole] = None
    hasAccessCondition: List[AccessCondition] = None
    targetAudience: List[Audience] = None
    hasOffer: List[Offer] = None
    hasImage: List[Image] = None
    hasOnlineContactPoint: List[OnlineContactPoint] = None
    hasReview: List[Review] = None
    subEventOf: List[PublicEvent] = None
    superEventOf: List[PublicEvent] = None
    hasPlaybill: Playbill = None
    eventTitle: List[Literal] = None
    description: List[Literal] = None
    eventAbstract: List[Literal] = None
    eventContentKeyword: List[Literal] = None
    shortEventTitle: List[Literal] = None
    identifier: Literal = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.hasPublicEventTypology:
            for hasPublicEventTypology in self.hasPublicEventTypology:
                g.add(
                    (self.uriRef, CPEV["hasPublicEventTypology"], hasPublicEventTypology.uriRef))

        if self.takesPlaceIn:
            for takesPlaceIn in self.takesPlaceIn:
                g.add((self.uriRef, CPEV["takesPlaceIn"], takesPlaceIn.uriRef))

        if self.hasRiT:
            for hasRiT in self.hasRiT:
                g.add((self.uriRef, RO["hasRiT"], hasRiT.uriRef))

        if self.hasAccessCondition:
            for hasAccessCondition in self.hasAccessCondition:
                g.add(
                    (self.uriRef, ACOND["hasAccessCondition"], hasAccessCondition.uriRef))

        if self.targetAudience:
            for targetAudience in self.targetAudience:
                g.add(
                    (self.uriRef, CPEV["targetAudience"], targetAudience.uriRef))

        if self.hasOffer:
            for hasOffer in self.hasOffer:
                g.add((self.uriRef, POT["hasOffer"], hasOffer.uriRef))

        if self.hasImage:
            for hasImage in self.hasImage:
                g.add((self.uriRef, SM["hasImage"], hasImage.uriRef))

        if self.hasOnlineContactPoint:
            for hasOnlineContactPoint in self.hasOnlineContactPoint:
                g.add(
                    (self.uriRef, SM["hasOnlineContactPoint"], hasOnlineContactPoint.uriRef))

        if self.hasReview:
            for hasReview in self.hasReview:
                g.add((self.uriRef, SM["hasReview"], hasReview.uriRef))

        if self.subEventOf:
            for subEventOf in self.subEventOf:
                g.add((self.uriRef, CPEV["subEventOf"], subEventOf.uriRef))

        if self.superEventOf:
            for superEventOf in self.superEventOf:
                g.add((self.uriRef, CPEV["superEventOf"], superEventOf.uriRef))

        if self.hasPlaybill:
            g.add((self.uriRef, CPEV["hasPlaybill"], self.hasPlaybill.uriRef))

        if self.eventTitle:
            for eventTitle in self.eventTitle:
                g.add((self.uriRef, CPEV["eventTitle"], eventTitle))

        if self.description:
            for description in self.description:
                g.add((self.uriRef, L0["description"], description))

        if self.eventAbstract:
            for eventAbstract in self.eventAbstract:
                g.add((self.uriRef, CPEV["eventAbstract"], eventAbstract))

        if self.eventContentKeyword:
            for eventContentKeyword in self.eventContentKeyword:
                g.add(
                    (self.uriRef, CPEV["eventContentKeyword"], eventContentKeyword))

        if self.shortEventTitle:
            for shortEventTitle in self.shortEventTitle:
                g.add((self.uriRef, CPEV["shortEventTitle"], shortEventTitle))

        if self.identifier:
            g.add((self.uriRef, L0["identifier"], self.identifier))
