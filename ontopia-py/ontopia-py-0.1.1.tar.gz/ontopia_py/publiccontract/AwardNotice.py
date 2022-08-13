from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..ns import *
from .Notice import Notice

if TYPE_CHECKING:
    from rdflib import Graph, Literal

    from ..l0.Agent import Agent


class AwardNotice(Notice):
    __type__ = PUBC["AwardNotice"]

    winner: List[Agent] = None
    agreedAmount: List[Literal] = None
    outcomeDate: List[Literal] = None
    reductionPercentage: List[Literal] = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.winner:
            for winner in self.winner:
                g.add((self.uriRef, PUBC["winner"], winner.uriRef))

        if self.agreedAmount:
            for agreedAmount in self.agreedAmount:
                g.add((self.uriRef, PUBC["agreedAmount"], agreedAmount))

        if self.outcomeDate:
            for outcomeDate in self.outcomeDate:
                g.add((self.uriRef, PUBC["outcomeDate"], outcomeDate))

        if self.reductionPercentage:
            for reductionPercentage in self.reductionPercentage:
                g.add(
                    (self.uriRef, PUBC["reductionPercentage"], reductionPercentage))
