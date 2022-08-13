from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..ns import *
from .CreativeWork import CreativeWork

if TYPE_CHECKING:
    from rdflib import Graph, Literal


class VideoObject(CreativeWork):
    __type__ = CIS["VideoObject"]

    URL: List[Literal] = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.URL:
            for URL in self.URL:
                g.add((self.uriRef, SM["URL"], URL))
