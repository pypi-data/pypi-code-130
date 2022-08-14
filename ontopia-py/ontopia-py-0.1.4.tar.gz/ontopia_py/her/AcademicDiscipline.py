from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..ns import *
from .HERClassification import HERClassification

if TYPE_CHECKING:
    from rdflib import Graph, Literal


class AcademicDiscipline(HERClassification):
    __type__ = HER["AcademicDiscipline"]

    name: List[Literal] = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.name:
            for name in self.name:
                g.add((self.uriRef, L0["name"], name))
