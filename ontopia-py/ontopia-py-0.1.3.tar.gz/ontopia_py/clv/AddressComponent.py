from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..ns import *
from .Feature import Feature

if TYPE_CHECKING:
    from rdflib import Graph


class AddressComponent(Feature):
    __type__ = CLV["AddressComponent"]

    situatedWithin: List[AddressComponent] = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.situatedWithin:
            for situatedWithin in self.situatedWithin:
                g.add(
                    (self.uriRef, CLV["situatedWithin"], situatedWithin.uriRef))
