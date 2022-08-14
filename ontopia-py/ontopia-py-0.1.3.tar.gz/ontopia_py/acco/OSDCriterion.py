from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..l0.Characteristic import Characteristic
from ..ns import *

if TYPE_CHECKING:
    from rdflib import Graph, Literal


class OSDCriterion(Characteristic):
    __type__ = ACCO["OSDCriterion"]

    criterion: List[Literal] = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.criterion:
            for criterion in self.criterion:
                g.add((self.uriRef, ACCO["criterion"], criterion))
