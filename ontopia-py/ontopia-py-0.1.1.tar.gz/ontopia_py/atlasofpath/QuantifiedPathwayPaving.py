from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..l0.Object import Object
from ..ns import *

if TYPE_CHECKING:
    from rdflib import Graph, Literal

    from .Path import Path
    from .Pathway import Pathway
    from .Paving import Paving


class QuantifiedPathwayPaving(Object):
    __type__ = PATHS["QuantifiedPathwayPaving"]

    isQuantifiedPathwayPavingOf: List[Path] = None
    forPathway: Pathway = None
    withPaving: Paving = None
    maxPercentage: Literal = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.isQuantifiedPathwayPavingOf:
            for isQuantifiedPathwayPavingOf in self.isQuantifiedPathwayPavingOf:
                g.add(
                    (self.uriRef, PATHS["isQuantifiedPathwayPavingOf"], isQuantifiedPathwayPavingOf.uriRef))

        if self.forPathway:
            g.add((self.uriRef, PATHS["forPathway"], self.forPathway.uriRef))

        if self.withPaving:
            g.add((self.uriRef, PATHS["withPaving"], self.withPaving.uriRef))

        if self.maxPercentage:
            g.add((self.uriRef, MU["maxPercentage"], self.maxPercentage))
