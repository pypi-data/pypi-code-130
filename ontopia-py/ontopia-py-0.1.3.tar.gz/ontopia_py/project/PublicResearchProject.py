from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..ns import *
from .PublicInvestmentProject import PublicInvestmentProject

if TYPE_CHECKING:
    from rdflib import Graph

    from .WorkPackage import WorkPackage


class PublicResearchProject(PublicInvestmentProject):
    __type__ = PROJ["PublicResearchProject"]

    hasWorkPackage: List[WorkPackage] = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.hasWorkPackage:
            for hasWorkPackage in self.hasWorkPackage:
                g.add(
                    (self.uriRef, PROJ["hasWorkPackage"], hasWorkPackage.uriRef))
