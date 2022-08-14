from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..l0.System import System
from ..ns import *

if TYPE_CHECKING:
    from rdflib import Graph, Literal

    from .Rule import Rule


class FormalFramework(System):
    __type__ = CPSV["FormalFramework"]

    name: List[Literal] = None
    referenceDoc: List[Literal] = None
    description: List[Literal] = None
    identifier: Literal = None
    isImplementedByRule: List[Rule] = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.isImplementedByRule:
            for isImplementedByRule in self.isImplementedByRule:
                g.add(
                    (self.uriRef, CPSV["isImplementedByRule"], isImplementedByRule.uriRef))

        if self.name:
            for name in self.name:
                g.add((self.uriRef, L0["name"], name))

        if self.referenceDoc:
            for referenceDoc in self.referenceDoc:
                g.add((self.uriRef, CPSV["referenceDoc"], referenceDoc))

        if self.description:
            for description in self.description:
                g.add((self.uriRef, L0["description"], description))

        if self.identifier:
            g.add((self.uriRef, L0["identifier"], self.identifier))
