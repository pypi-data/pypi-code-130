from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..ns import *
from .Post import Post

if TYPE_CHECKING:
    from rdflib import Graph, Literal

    from .Rating import Rating


class Review(Post):
    __type__ = SM["Review"]

    hasRating: List[Rating] = None
    reviewAspect: Literal = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.hasRating:
            for hasRating in self.hasRating:
                g.add((self.uriRef, SM["hasRating"], hasRating.uriRef))

        if self.reviewAspect:
            g.add((self.uriRef, SM["reviewAspect"], self.reviewAspect))
