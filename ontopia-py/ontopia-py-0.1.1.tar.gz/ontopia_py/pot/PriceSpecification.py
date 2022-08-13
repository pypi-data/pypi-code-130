from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..l0.Characteristic import Characteristic
from ..ns import *

if TYPE_CHECKING:
    from rdflib import Graph, Literal

    from .Currency import Currency


class PriceSpecification(Characteristic):
    __type__ = POT["PriceSpecification"]

    hasCurrency: List[Currency] = None
    hasCurrencyValue: List[Literal] = None
    VAT: Literal = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.hasCurrency:
            for hasCurrency in self.hasCurrency:
                g.add((self.uriRef, POT["hasCurrency"], hasCurrency.uriRef))

        if self.hasCurrencyValue:
            for hasCurrencyValue in self.hasCurrencyValue:
                g.add((self.uriRef, POT["hasCurrencyValue"], hasCurrencyValue))

        if self.VAT:
            g.add((self.uriRef, POT["VAT"], self.VAT))
