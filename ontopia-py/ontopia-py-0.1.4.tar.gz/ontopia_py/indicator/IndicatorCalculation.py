from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..l0.Activity import Activity
from ..ns import *

if TYPE_CHECKING:
    from rdflib import Graph, Literal

    from ..l0.Entity import Entity
    from ..mu.Value import Value
    from ..ti.TimeInterval import TimeInterval
    from .AccrualPeriodicity import AccrualPeriodicity
    from .CalculationMethod import CalculationMethod
    from .DatumSource import DatumSource
    from .Indicator import Indicator
    from .Metric import Metric


class IndicatorCalculation(Activity):
    __type__ = INDIC["IndicatorCalculation"]

    basedOnMetric: List[Metric] = None
    hasDatumSource: List[DatumSource] = None
    isIndicatorCalculationOf: List[Entity] = None
    computedAtTime: List[TimeInterval] = None
    hasCalculationMethod: List[CalculationMethod] = None
    forIndicator: Indicator = None
    hasIndicatorValue: Value = None
    hasAccrualPeriodicity: AccrualPeriodicity = None
    communcatedAt: Literal = None
    modified: Literal = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.basedOnMetric:
            for basedOnMetric in self.basedOnMetric:
                g.add(
                    (self.uriRef, INDIC["basedOnMetric"], basedOnMetric.uriRef))

        if self.hasDatumSource:
            for hasDatumSource in self.hasDatumSource:
                g.add(
                    (self.uriRef, INDIC["hasDatumSource"], hasDatumSource.uriRef))

        if self.isIndicatorCalculationOf:
            for isIndicatorCalculationOf in self.isIndicatorCalculationOf:
                g.add(
                    (self.uriRef, INDIC["isIndicatorCalculationOf"], isIndicatorCalculationOf.uriRef))

        if self.computedAtTime:
            for computedAtTime in self.computedAtTime:
                g.add(
                    (self.uriRef, INDIC["computedAtTime"], computedAtTime.uriRef))

        if self.hasCalculationMethod:
            for hasCalculationMethod in self.hasCalculationMethod:
                g.add(
                    (self.uriRef, INDIC["hasCalculationMethod"], hasCalculationMethod.uriRef))

        if self.forIndicator:
            g.add((self.uriRef, INDIC["forIndicator"],
                  self.forIndicator.uriRef))

        if self.hasIndicatorValue:
            g.add(
                (self.uriRef, INDIC["hasIndicatorValue"], self.hasIndicatorValue.uriRef))

        if self.hasAccrualPeriodicity:
            g.add(
                (self.uriRef, INDIC["hasAccrualPeriodicity"], self.hasAccrualPeriodicity.uriRef))

        if self.communcatedAt:
            g.add((self.uriRef, INDIC["communcatedAt"], self.communcatedAt))

        if self.modified:
            g.add((self.uriRef, TI["modified"], self.modified))
