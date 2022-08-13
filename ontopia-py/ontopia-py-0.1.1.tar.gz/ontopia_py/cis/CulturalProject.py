from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..l0.Activity import Activity
from ..ns import *

if TYPE_CHECKING:
    from rdflib import Graph, Literal


class CulturalProject(Activity):
    __type__ = CIS["CulturalProject"]

    URL: List[Literal] = None
    name: List[Literal] = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.URL:
            for URL in self.URL:
                g.add((self.uriRef, SM["URL"], URL))

        if self.name:
            for name in self.name:
                g.add((self.uriRef, L0["name"], name))
