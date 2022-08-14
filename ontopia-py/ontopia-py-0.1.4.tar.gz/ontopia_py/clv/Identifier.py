from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..l0 import Characteristic
from ..ns import *

if TYPE_CHECKING:
    from rdflib import Graph, Literal

    from ..cov.Organization import Organization


class Identifier(Characteristic):
    __type__ = CLV["Identifier"]

    issuedBy: List[Organization] = None
    identifier: Literal = None
    identifierType: Literal = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.issuedBy:
            for issuedBy in self.issuedBy:
                g.add((self.uriRef, CLV["issuedBy"], issuedBy.uriRef))

        if self.identifier:
            g.add((self.uriRef, L0["identifier"], self.identifier))

        if self.identifierType:
            g.add((self.uriRef, CLV["identifierType"], self.identifierType))
