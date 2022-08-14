from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..l0.Characteristic import Characteristic
from ..ns import *

if TYPE_CHECKING:
    from rdflib import Graph, Literal

    from .ProcedureChangeEvent import ProcedureChangeEvent


class EconomicSummary(Characteristic):
    __type__ = PUBC["EconomicSummary"]

    changedByProcedureChangeEvent: List[ProcedureChangeEvent] = None
    resultedFrom: List[ProcedureChangeEvent] = None
    availableAmount: List[Literal] = None
    estimatedEndDate: List[Literal] = None
    planningAmount: List[Literal] = None
    safetyAmount: List[Literal] = None
    servicesAmount: List[Literal] = None
    nonDiscountableSum: List[Literal] = None
    suppliesAmount: List[Literal] = None
    totalAmount: List[Literal] = None
    worksAmount: List[Literal] = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.changedByProcedureChangeEvent:
            for changedByProcedureChangeEvent in self.changedByProcedureChangeEvent:
                g.add((self.uriRef, PUBC["changedByProcedureChangeEvent"],
                      changedByProcedureChangeEvent.uriRef))

        if self.resultedFrom:
            for resultedFrom in self.resultedFrom:
                g.add((self.uriRef, PUBC["resultedFrom"], resultedFrom.uriRef))

        if self.availableAmount:
            for availableAmount in self.availableAmount:
                g.add((self.uriRef, PUBC["availableAmount"], availableAmount))

        if self.estimatedEndDate:
            for estimatedEndDate in self.estimatedEndDate:
                g.add(
                    (self.uriRef, PUBC["estimatedEndDate"], estimatedEndDate))

        if self.planningAmount:
            for planningAmount in self.planningAmount:
                g.add((self.uriRef, PUBC["planningAmount"], planningAmount))

        if self.safetyAmount:
            for safetyAmount in self.safetyAmount:
                g.add((self.uriRef, PUBC["safetyAmount"], safetyAmount))

        if self.servicesAmount:
            for servicesAmount in self.servicesAmount:
                g.add((self.uriRef, PUBC["servicesAmount"], servicesAmount))

        if self.nonDiscountableSum:
            for nonDiscountableSum in self.nonDiscountableSum:
                g.add(
                    (self.uriRef, PUBC["nonDiscountableSum"], nonDiscountableSum))

        if self.suppliesAmount:
            for suppliesAmount in self.suppliesAmount:
                g.add((self.uriRef, PUBC["suppliesAmount"], suppliesAmount))

        if self.totalAmount:
            for totalAmount in self.totalAmount:
                g.add((self.uriRef, PUBC["totalAmount"], totalAmount))

        if self.worksAmount:
            for worksAmount in self.worksAmount:
                g.add((self.uriRef, PUBC["worksAmount"], worksAmount))
