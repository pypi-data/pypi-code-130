from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..l0.Description import Description
from ..ns import *

if TYPE_CHECKING:
    from rdflib import Graph, Literal

    from ..clv.Feature import Feature
    from ..cov.Organization import Organization
    from ..l0.Agent import Agent
    from ..l0.Entity import Entity
    from ..ro.TimeIndexedRole import TimeIndexedRole
    from ..sm.OnlineContactPoint import OnlineContactPoint
    from ..ti.Duration import Duration
    from .Call import Call
    from .Programme import Programme
    from .Summary import Summary
    from .UniqueProjectCode import UniqueProjectCode


class PublicInvestmentProject(Description):
    __type__ = PROJ["PublicInvestmentProject"]

    hasProgramme: List[Programme] = None
    projectFunder: List[Organization] = None
    hasSpatialCoverage: List[Feature] = None
    hasParticipantingAgent: List[Agent] = None
    hasRiT: List[TimeIndexedRole] = None
    involvesEntity: List[Entity] = None
    hasDuration: Duration = None
    hasCall: Call = None
    hasSummary: Summary = None
    hasUniqueProjectCode: UniqueProjectCode = None
    hasOnlineContactPoint: OnlineContactPoint = None
    projectTitle: List[Literal] = None
    projectKeyword: List[Literal] = None
    uniqueProjectCodeValue: Literal = None
    projectAcronym: Literal = None
    projectTotalCost: Literal = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.hasProgramme:
            for hasProgramme in self.hasProgramme:
                g.add((self.uriRef, PROJ["hasProgramme"], hasProgramme.uriRef))

        if self.projectFunder:
            for projectFunder in self.projectFunder:
                g.add(
                    (self.uriRef, PROJ["projectFunder"], projectFunder.uriRef))

        if self.hasSpatialCoverage:
            for hasSpatialCoverage in self.hasSpatialCoverage:
                g.add(
                    (self.uriRef, CLV["hasSpatialCoverage"], hasSpatialCoverage.uriRef))

        if self.hasParticipantingAgent:
            for hasParticipantingAgent in self.hasParticipantingAgent:
                g.add(
                    (self.uriRef, PROJ["hasParticipantingAgent"], hasParticipantingAgent.uriRef))

        if self.hasRiT:
            for hasRiT in self.hasRiT:
                g.add((self.uriRef, RO["hasRiT"], hasRiT.uriRef))

        if self.involvesEntity:
            for involvesEntity in self.involvesEntity:
                g.add(
                    (self.uriRef, PROJ["involvesEntity"], involvesEntity.uriRef))

        if self.hasDuration:
            g.add((self.uriRef, TI["hasDuration"], self.hasDuration.uriRef))

        if self.hasCall:
            g.add((self.uriRef, PROJ["hasCall"], self.hasCall.uriRef))

        if self.hasSummary:
            g.add((self.uriRef, PROJ["hasSummary"], self.hasSummary.uriRef))

        if self.hasUniqueProjectCode:
            g.add(
                (self.uriRef, PROJ["hasUniqueProjectCode"], self.hasUniqueProjectCode.uriRef))

        if self.hasOnlineContactPoint:
            g.add((self.uriRef, SM["hasOnlineContactPoint"],
                  self.hasOnlineContactPoint.uriRef))

        if self.projectTitle:
            for projectTitle in self.projectTitle:
                g.add((self.uriRef, PROJ["projectTitle"], projectTitle))

        if self.projectKeyword:
            for projectKeyword in self.projectKeyword:
                g.add((self.uriRef, PROJ["projectKeyword"], projectKeyword))

        if self.uniqueProjectCodeValue:
            g.add(
                (self.uriRef, PROJ["uniqueProjectCodeValue"], self.uniqueProjectCodeValue))

        if self.projectAcronym:
            g.add((self.uriRef, PROJ["projectAcronym"], self.projectAcronym))

        if self.projectTotalCost:
            g.add(
                (self.uriRef, PROJ["projectTotalCost"], self.projectTotalCost))
