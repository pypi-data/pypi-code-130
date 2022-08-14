from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..l0.Characteristic import Characteristic
from ..ns import *

if TYPE_CHECKING:
    from rdflib import Graph, Literal


class LegalStatus(Characteristic):
    __type__ = COV["LegalStatus"]

    legalStatusCode: List[Literal] = None
    legalStatusDesc: List[Literal] = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.legalStatusCode:
            for legalStatusCode in self.legalStatusCode:
                g.add((self.uriRef, COV["legalStatusCode"], legalStatusCode))

        if self.legalStatusDesc:
            for legalStatusDesc in self.legalStatusDesc:
                g.add((self.uriRef, COV["legalStatusDesc"], legalStatusDesc))
