from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..ns import *
from .Document import Document

if TYPE_CHECKING:
    from rdflib import Graph

    from ..l0.Agent import Agent
    from ..ro.TimeIndexedRole import TimeIndexedRole
    from .AmendmentDocument import AmendmentDocument
    from .CommonProcurementVocabulary import CommonProcurementVocabulary
    from .EconomicSummary import EconomicSummary
    from .FrameworkAgreement import FrameworkAgreement
    from .Resolution import Resolution
    from .Tender import Tender


class Contract(Document):
    __type__ = PUBC["Contract"]

    hasCPV: List[CommonProcurementVocabulary] = None
    refersToTender: List[Tender] = None
    hasChangeDocument: List[AmendmentDocument] = None
    hasContractualResolution: List[Resolution] = None
    hasEconomicSummary: List[EconomicSummary] = None
    winner: List[Agent] = None
    holdsRoleInTime: List[TimeIndexedRole] = None
    hasFrameworkAgreement: FrameworkAgreement = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.hasCPV:
            for hasCPV in self.hasCPV:
                g.add((self.uriRef, PUBC["hasCPV"], hasCPV.uriRef))

        if self.refersToTender:
            for refersToTender in self.refersToTender:
                g.add(
                    (self.uriRef, PUBC["refersToTender"], refersToTender.uriRef))

        if self.hasChangeDocument:
            for hasChangeDocument in self.hasChangeDocument:
                g.add(
                    (self.uriRef, PUBC["hasChangeDocument"], hasChangeDocument.uriRef))

        if self.hasContractualResolution:
            for hasContractualResolution in self.hasContractualResolution:
                g.add(
                    (self.uriRef, PUBC["hasContractualResolution"], hasContractualResolution.uriRef))

        if self.hasEconomicSummary:
            for hasEconomicSummary in self.hasEconomicSummary:
                g.add(
                    (self.uriRef, PUBC["hasEconomicSummary"], hasEconomicSummary.uriRef))

        if self.winner:
            for winner in self.winner:
                g.add((self.uriRef, PUBC["winner"], winner.uriRef))

        if self.holdsRoleInTime:
            for holdsRoleInTime in self.holdsRoleInTime:
                g.add(
                    (self.uriRef, RO["holdsRoleInTime"], holdsRoleInTime.uriRef))

        if self.hasFrameworkAgreement:
            g.add((self.uriRef, PUBC["hasFrameworkAgreement"],
                  self.hasFrameworkAgreement.uriRef))
