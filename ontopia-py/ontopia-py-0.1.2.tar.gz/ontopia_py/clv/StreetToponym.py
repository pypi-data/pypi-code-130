from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..ns import *
from .AddressComponent import AddressComponent

if TYPE_CHECKING:
    from rdflib import Graph, Literal


class StreetToponym(AddressComponent):
    __type__ = CLV["StreetToponym"]

    officialStreetName: List[Literal] = None
    toponymQualifier: List[Literal] = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.officialStreetName:
            for officialStreetName in self.officialStreetName:
                g.add(
                    (self.uriRef, CLV["officialStreetName"], officialStreetName))

        if self.toponymQualifier:
            for toponymQualifier in self.toponymQualifier:
                g.add((self.uriRef, CLV["toponymQualifier"], toponymQualifier))
