from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..l0.Activity import Activity
from ..ns import *

if TYPE_CHECKING:
    from rdflib import Graph, Literal

    from ..l0.Agent import Agent
    from .TransparencyActivityTypology import TransparencyActivityTypology
    from .TransparencyObligation import TransparencyObligation
    from .TransparencyResource import TransparencyResource


class TransparencyActivity(Activity):
    __type__ = TRANSP["TransparencyActivity"]

    generatesResource: List[TransparencyResource] = None
    hasTransparencyActivityTypology: List[TransparencyActivityTypology] = None
    triggeredBy: List[TransparencyObligation] = None
    isPerformedByAgent: Agent = None
    date: Literal = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.generatesResource:
            for generatesResource in self.generatesResource:
                g.add(
                    (self.uriRef, TRANSP["generatesResource"], generatesResource.uriRef))

        if self.hasTransparencyActivityTypology:
            for hasTransparencyActivityTypology in self.hasTransparencyActivityTypology:
                g.add((self.uriRef, TRANSP["hasTransparencyActivityTypology"],
                      hasTransparencyActivityTypology.uriRef))

        if self.triggeredBy:
            for triggeredBy in self.triggeredBy:
                g.add((self.uriRef, TRANSP["triggeredBy"], triggeredBy.uriRef))

        if self.isPerformedByAgent:
            g.add(
                (self.uriRef, TRANSP["isPerformedByAgent"], self.isPerformedByAgent.uriRef))

        if self.date:
            g.add((self.uriRef, TI["date"], self.date))
