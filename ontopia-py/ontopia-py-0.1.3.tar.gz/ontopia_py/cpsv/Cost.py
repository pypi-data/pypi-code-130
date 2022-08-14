from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..l0.Characteristic import Characteristic
from ..ns import *

if TYPE_CHECKING:
    from rdflib import Graph, Literal


class Cost(Characteristic):
    __type__ = CPSV["Cost"]

    description: List[Literal] = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.description:
            for description in self.description:
                g.add((self.uriRef, L0["description"], description))
