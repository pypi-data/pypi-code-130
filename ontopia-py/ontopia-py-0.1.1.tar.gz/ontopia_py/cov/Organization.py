from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..l0.Agent import Agent
from ..ns import *

if TYPE_CHECKING:
    from rdflib import Graph, Literal

    from ..clv.Address import Address
    from ..clv.Identifier import Identifier
    from ..l0.Location import Location
    from ..sm.Image import Image
    from ..sm.OnlineContactPoint import OnlineContactPoint
    from ..Thing import Thing
    from .ActivityType import ActivityType
    from .BalanceSheet import BalanceSheet
    from .ChangeEvent import ChangeEvent
    from .Employment import Employment
    from .LegalStatus import LegalStatus
    from .SupportUnit import SupportUnit


class Organization(Agent):
    __type__ = COV["Organization"]

    hasSpatialCoverage: List[Location] = None
    changedBy: List[ChangeEvent] = None
    hasActivityType: List[ActivityType] = None
    hasAlternativeIdentifier: List[Identifier] = None
    hasBalanceSheet: List[BalanceSheet] = None
    holdEmployment: List[Employment] = None
    participating: List[Organization] = None
    resultedFrom: List[ChangeEvent] = None
    hasPrimaryAddress: Address = None
    hasLegalStatus: LegalStatus = None
    hasOnlineContactPoint: OnlineContactPoint = None
    hasLogo: Image = None
    legalName: List[Literal] = None
    description: List[Literal] = None
    mainFunction: List[Literal] = None
    taxCode: Literal = None
    accreditationDate: Literal = None
    altName: Literal = None
    foundationDate: Literal = None
    orgAcronym: Literal = None
    follows: List[Organization] = None
    hasSupportUnit: List[SupportUnit] = None
    hasSubOrganization: List[Organization] = None
    isOrganizationOf: List[Thing] = None
    precedes: List[Organization] = None
    subOrganizationOf: List[Organization] = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.hasSpatialCoverage:
            for hasSpatialCoverage in self.hasSpatialCoverage:
                g.add(
                    (self.uriRef, CLV["hasSpatialCoverage"], hasSpatialCoverage.uriRef))

        if self.changedBy:
            for changedBy in self.changedBy:
                g.add((self.uriRef, COV["changedBy"], changedBy.uriRef))

        if self.hasActivityType:
            for hasActivityType in self.hasActivityType:
                g.add(
                    (self.uriRef, COV["hasActivityType"], hasActivityType.uriRef))

        if self.hasAlternativeIdentifier:
            for hasAlternativeIdentifier in self.hasAlternativeIdentifier:
                g.add(
                    (self.uriRef, COV["hasAlternativeIdentifier"], hasAlternativeIdentifier.uriRef))

        if self.hasBalanceSheet:
            for hasBalanceSheet in self.hasBalanceSheet:
                g.add(
                    (self.uriRef, COV["hasBalanceSheet"], hasBalanceSheet.uriRef))

        if self.holdEmployment:
            for holdEmployment in self.holdEmployment:
                g.add(
                    (self.uriRef, COV["holdEmployment"], holdEmployment.uriRef))

        if self.participating:
            for participating in self.participating:
                g.add(
                    (self.uriRef, COV["participating"], participating.uriRef))

        if self.resultedFrom:
            for resultedFrom in self.resultedFrom:
                g.add((self.uriRef, COV["resultedFrom"], resultedFrom.uriRef))

        if self.legalName:
            for legalName in self.legalName:
                g.add((self.uriRef, COV["legalName"], legalName))

        if self.description:
            for description in self.description:
                g.add((self.uriRef, L0["description"], description))

        if self.mainFunction:
            for mainFunction in self.mainFunction:
                g.add((self.uriRef, COV["mainFunction"], mainFunction))

        if self.follows:
            for follows in self.follows:
                g.add((self.uriRef, COV["follows"], follows.uriRef))

        if self.hasSupportUnit:
            for hasSupportUnit in self.hasSupportUnit:
                g.add(
                    (self.uriRef, COV["hasSupportUnit"], hasSupportUnit.uriRef))

        if self.hasSubOrganization:
            for hasSubOrganization in self.hasSubOrganization:
                g.add(
                    (self.uriRef, COV["hasSubOrganization"], hasSubOrganization.uriRef))

        if self.isOrganizationOf:
            for isOrganizationOf in self.isOrganizationOf:
                g.add(
                    (self.uriRef, COV["isOrganizationOf"], isOrganizationOf.uriRef))

        if self.precedes:
            for precedes in self.precedes:
                g.add((self.uriRef, COV["precedes"], precedes.uriRef))

        if self.subOrganizationOf:
            for subOrganizationOf in self.subOrganizationOf:
                g.add(
                    (self.uriRef, COV["subOrganizationOf"], subOrganizationOf.uriRef))

        if self.hasPrimaryAddress:
            g.add((self.uriRef, CLV["hasPrimaryAddress"],
                  self.hasPrimaryAddress.uriRef))

        if self.hasLegalStatus:
            g.add((self.uriRef, COV["hasLegalStatus"],
                  self.hasLegalStatus.uriRef))

        if self.hasOnlineContactPoint:
            g.add((self.uriRef, SM["hasOnlineContactPoint"],
                  self.hasOnlineContactPoint.uriRef))

        if self.hasLogo:
            g.add((self.uriRef, COV["hasLogo"], self.hasLogo.uriRef))

        if self.taxCode:
            g.add((self.uriRef, COV["taxCode"], self.taxCode))

        if self.accreditationDate:
            g.add(
                (self.uriRef, COV["accreditationDate"], self.accreditationDate))

        if self.altName:
            g.add((self.uriRef, COV["altName"], self.altName))

        if self.foundationDate:
            g.add((self.uriRef, COV["foundationDate"], self.foundationDate))

        if self.orgAcronym:
            g.add((self.uriRef, COV["orgAcronym"], self.orgAcronym))
