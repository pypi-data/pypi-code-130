from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..ns import *
from .Notice import Notice

if TYPE_CHECKING:
    from rdflib import Graph, Literal


class CallForCompetition(Notice):
    __type__ = PUBC["CallForCompetition"]

    expireDate: List[Literal] = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.expireDate:
            for expireDate in self.expireDate:
                g.add(
                    (self.uriRef, PUBC["expireDate"], expireDate))
