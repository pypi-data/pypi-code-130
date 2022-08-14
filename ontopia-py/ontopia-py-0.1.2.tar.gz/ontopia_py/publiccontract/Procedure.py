from __future__ import annotations

from typing import TYPE_CHECKING, List, Literal

from ..ns import *
from .ProcurementProject import ProcurementProject

if TYPE_CHECKING:
    from rdflib import Graph

    from ..l0.Agent import Agent
    from ..ro.TimeIndexedRole import TimeIndexedRole
    from .CommonProcurementVocabulary import CommonProcurementVocabulary
    from .Lot import Lot
    from .ProcedureType import ProcedureType
    from .ProcurementDocument import ProcurementDocument
    from .ResolutionToContract import ResolutionToContract


class Procedure(ProcurementProject):
    __type__ = PUBC["Procedure"]

    hasCPV: List[CommonProcurementVocabulary] = None
    hasProcurementDocument: List[ProcurementDocument] = None
    includesLot: List[Lot] = None
    holdsRoleInTime: List[TimeIndexedRole] = None
    hasResolutionToContract: List[ResolutionToContract] = None
    hasProcedureType: List[ProcedureType] = None
    hasProcuringEntity: Agent = None
    procedureTotalAmount: List[Literal] = None
    identifier: Literal = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.hasCPV:
            for hasCPV in self.hasCPV:
                g.add((self.uriRef, PUBC["hasCPV"], hasCPV.uriRef))

        if self.hasProcurementDocument:
            for hasProcurementDocument in self.hasProcurementDocument:
                g.add(
                    (self.uriRef, PUBC["hasProcurementDocument"], hasProcurementDocument.uriRef))

        if self.includesLot:
            for includesLot in self.includesLot:
                g.add((self.uriRef, PUBC["includesLot"], includesLot.uriRef))

        if self.holdsRoleInTime:
            for holdsRoleInTime in self.holdsRoleInTime:
                g.add(
                    (self.uriRef, RO["holdsRoleInTime"], holdsRoleInTime.uriRef))

        if self.hasResolutionToContract:
            for hasResolutionToContract in self.hasResolutionToContract:
                g.add(
                    (self.uriRef, PUBC["hasResolutionToContract"], hasResolutionToContract.uriRef))

        if self.hasProcedureType:
            for hasProcedureType in self.hasProcedureType:
                g.add(
                    (self.uriRef, PUBC["hasProcedureType"], hasProcedureType.uriRef))

        if self.hasProcuringEntity:
            g.add((self.uriRef, PUBC["hasProcuringEntity"],
                  self.hasProcuringEntity.uriRef))

        if self.procedureTotalAmount:
            for procedureTotalAmount in self.procedureTotalAmount:
                g.add(
                    (self.uriRef, PUBC["procedureTotalAmount"], procedureTotalAmount))

        if self.identifier:
            g.add((self.uriRef, PUBC["identifier"], self.identifier))
