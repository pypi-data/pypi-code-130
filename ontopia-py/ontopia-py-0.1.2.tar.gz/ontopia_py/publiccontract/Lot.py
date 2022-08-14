from __future__ import annotations

from typing import TYPE_CHECKING, List, Literal

from ..ns import *
from .ProcurementProject import ProcurementProject

if TYPE_CHECKING:
    from rdflib import Graph

    from .AwardCriterion import AwardCriterion
    from .AwardNotice import AwardNotice
    from .Contract import Contract
    from .CommonProcurementVocabulary import CommonProcurementVocabulary
    from .PaymentCertificate import PaymentCertificate
    from .Procedure import Procedure
    from .WorkProgressReport import WorkProgressReport


class Contract(ProcurementProject):
    __type__ = PUBC["Contract"]

    hasCPV: List[CommonProcurementVocabulary] = None
    hasContract: List[Contract] = None
    hasAwardCriterion: List[AwardCriterion] = None
    hasAwardNotice: List[AwardNotice] = None
    hasPaymentCertificate: List[PaymentCertificate] = None
    hasWorkProgressReport: List[WorkProgressReport] = None
    isIncludedInProcedure: Procedure = None
    actualEndDate: List[Literal] = None
    actualStartDate: List[Literal] = None
    currentAvailableAmount: List[Literal] = None
    currentEstimatedEndDate: List[Literal] = None
    currentPlanningAmount: List[Literal] = None
    currentSafetyAmount: List[Literal] = None
    currentServicesAmount: List[Literal] = None
    currentSuppliesAmount: List[Literal] = None
    currentTotalAmount: List[Literal] = None
    currentWorksAmount: List[Literal] = None
    specialSector: List[Literal] = None
    totalAmountPaid: List[Literal] = None
    CIG: Literal = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.hasCPV:
            for hasCPV in self.hasCPV:
                g.add((self.uriRef, PUBC["hasCPV"], hasCPV.uriRef))

        if self.hasContract:
            for hasContract in self.hasContract:
                g.add((self.uriRef, PUBC["hasContract"], hasContract.uriRef))

        if self.hasAwardCriterion:
            for hasAwardCriterion in self.hasAwardCriterion:
                g.add(
                    (self.uriRef, PUBC["hasAwardCriterion"], hasAwardCriterion.uriRef))

        if self.hasAwardNotice:
            for hasAwardNotice in self.hasAwardNotice:
                g.add(
                    (self.uriRef, PUBC["hasAwardNotice"], hasAwardNotice.uriRef))

        if self.hasPaymentCertificate:
            for hasPaymentCertificate in self.hasPaymentCertificate:
                g.add(
                    (self.uriRef, PUBC["hasPaymentCertificate"], hasPaymentCertificate.uriRef))

        if self.hasWorkProgressReport:
            for hasWorkProgressReport in self.hasWorkProgressReport:
                g.add(
                    (self.uriRef, PUBC["hasWorkProgressReport"], hasWorkProgressReport.uriRef))

        if self.isIncludedInProcedure:
            g.add((self.uriRef, PUBC["isIncludedInProcedure"],
                  self.isIncludedInProcedure.uriRef))

        if self.actualEndDate:
            for actualEndDate in self.actualEndDate:
                g.add((self.uriRef, PUBC["actualEndDate"], actualEndDate))

        if self.actualStartDate:
            for actualStartDate in self.actualStartDate:
                g.add((self.uriRef, PUBC["actualStartDate"], actualStartDate))

        if self.currentAvailableAmount:
            for currentAvailableAmount in self.currentAvailableAmount:
                g.add(
                    (self.uriRef, PUBC["currentAvailableAmount"], currentAvailableAmount))

        if self.currentEstimatedEndDate:
            for currentEstimatedEndDate in self.currentEstimatedEndDate:
                g.add(
                    (self.uriRef, PUBC["currentEstimatedEndDate"], currentEstimatedEndDate))

        if self.currentPlanningAmount:
            for currentPlanningAmount in self.currentPlanningAmount:
                g.add(
                    (self.uriRef, PUBC["currentPlanningAmount"], currentPlanningAmount))

        if self.currentSafetyAmount:
            for currentSafetyAmount in self.currentSafetyAmount:
                g.add(
                    (self.uriRef, PUBC["currentSafetyAmount"], currentSafetyAmount))

        if self.currentServicesAmount:
            for currentServicesAmount in self.currentServicesAmount:
                g.add(
                    (self.uriRef, PUBC["currentServicesAmount"], currentServicesAmount))

        if self.currentSuppliesAmount:
            for currentSuppliesAmount in self.currentSuppliesAmount:
                g.add(
                    (self.uriRef, PUBC["currentSuppliesAmount"], currentSuppliesAmount))

        if self.currentTotalAmount:
            for currentTotalAmount in self.currentTotalAmount:
                g.add(
                    (self.uriRef, PUBC["currentTotalAmount"], currentTotalAmount))

        if self.currentWorksAmount:
            for currentWorksAmount in self.currentWorksAmount:
                g.add(
                    (self.uriRef, PUBC["currentWorksAmount"], currentWorksAmount))

        if self.specialSector:
            for specialSector in self.specialSector:
                g.add((self.uriRef, PUBC["specialSector"], specialSector))

        if self.totalAmountPaid:
            for totalAmountPaid in self.totalAmountPaid:
                g.add((self.uriRef, PUBC["totalAmountPaid"], totalAmountPaid))

        if self.CIG:
            g.add((self.uriRef, PUBC["CIG"], self.CIG))
