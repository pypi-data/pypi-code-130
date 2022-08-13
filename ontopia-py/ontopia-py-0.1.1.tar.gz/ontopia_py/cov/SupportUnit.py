from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..ns import *
from .Organization import Organization

if TYPE_CHECKING:
    from rdflib import Graph, Literal


class SupportUnit(Organization):
    __type__ = COV["SupportUnit"]

    isSupportUnitOf: List[Organization] = None
    officeIdentifier: List[Literal] = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.isSupportUnitOf:
            for isSupportUnitOf in self.isSupportUnitOf:
                g.add(
                    (self.uriRef, COV["isSupportUnitOf"], isSupportUnitOf.uriRef))

        if self.officeIdentifier:
            for officeIdentifier in self.officeIdentifier:
                g.add((self.uriRef, COV["officeIdentifier"], officeIdentifier))
