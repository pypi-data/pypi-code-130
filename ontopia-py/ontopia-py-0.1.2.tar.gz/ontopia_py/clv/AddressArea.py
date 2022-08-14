from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..ns import *
from .AddressComponent import AddressComponent

if TYPE_CHECKING:
    from rdflib import Graph, Literal


class AddressArea(AddressComponent):
    __type__ = CLV["AddressArea"]

    name: List[Literal] = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.name:
            for name in self.name:
                g.add((self.uriRef, L0["name"], name))
