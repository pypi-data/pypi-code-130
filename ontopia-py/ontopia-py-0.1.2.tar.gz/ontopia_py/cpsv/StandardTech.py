from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..ns import *
from .Requirement import Requirement

if TYPE_CHECKING:
    from rdflib import Graph, Literal


class StandardTech(Requirement):
    __type__ = CPSV["StandardTech"]

    referenceDoc: List[Literal] = None
    description: List[Literal] = None
    identifier: Literal = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.referenceDoc:
            for referenceDoc in self.referenceDoc:
                g.add((self.uriRef, CPSV["referenceDoc"], referenceDoc))

        if self.description:
            for description in self.description:
                g.add((self.uriRef, L0["description"], description))

        if self.identifier:
            g.add((self.uriRef, L0["identifier"], self.identifier))
