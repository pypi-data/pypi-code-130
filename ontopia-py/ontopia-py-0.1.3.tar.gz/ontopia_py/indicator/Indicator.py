from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..l0.Characteristic import Characteristic
from ..ns import *

if TYPE_CHECKING:
    from rdflib import Graph, Literal

    from .IndicatorCalculation import IndicatorCalculation
    from .IndicatorType import IndicatorType
    from .Purpose import Purpose


class Indicator(Characteristic):
    __type__ = INDIC["Indicator"]

    meetsPurpose: List[Purpose] = None
    computedInIndicatorCalculation: List[IndicatorCalculation] = None
    subIndicator: List[Indicator] = None
    superIndicator: List[Indicator] = None
    hasIndicatorType: IndicatorType = None
    name: List[Literal] = None
    definedInLegislation: List[Literal] = None
    description: List[Literal] = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.meetsPurpose:
            for meetsPurpose in self.meetsPurpose:
                g.add(
                    (self.uriRef, INDIC["meetsPurpose"], meetsPurpose.uriRef))

        if self.computedInIndicatorCalculation:
            for computedInIndicatorCalculation in self.computedInIndicatorCalculation:
                g.add((self.uriRef, INDIC["computedInIndicatorCalculation"],
                      computedInIndicatorCalculation.uriRef))

        if self.subIndicator:
            for subIndicator in self.subIndicator:
                g.add(
                    (self.uriRef, INDIC["subIndicator"], subIndicator.uriRef))

        if self.superIndicator:
            for superIndicator in self.superIndicator:
                g.add(
                    (self.uriRef, INDIC["superIndicator"], superIndicator.uriRef))

        if self.hasIndicatorType:
            g.add(
                (self.uriRef, INDIC["hasIndicatorType"], self.hasIndicatorType.uriRef))

        if self.name:
            for name in self.name:
                g.add(
                    (self.uriRef, L0["name"], name))

        if self.definedInLegislation:
            for definedInLegislation in self.definedInLegislation:
                g.add(
                    (self.uriRef, INDIC["definedInLegislation"], definedInLegislation))

        if self.description:
            for description in self.description:
                g.add(
                    (self.uriRef, L0["description"], description))
