from __future__ import annotations

from typing import TYPE_CHECKING, List

from rdflib import URIRef

from ..l0.Description import Description
from ..ns import *

if TYPE_CHECKING:
    from rdflib import Graph

    from .PathPlan import PathPlan


class TravellingMethod(Description):
    __type__ = PATHS["TravellingMethod"]

    isTravellingMethodOf: List[PathPlan] = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.isTravellingMethodOf:
            for isTravellingMethodOf in self.isTravellingMethodOf:
                g.add(
                    (self.uriRef, PATHS["isTravellingMethodOf"], isTravellingMethodOf.uriRef))


class Cycling(TravellingMethod):
    def __init__(self):
        self.uriRef = URIRef(PATHS["Cycling"])


class Horseback(TravellingMethod):
    def __init__(self):
        self.uriRef = URIRef(PATHS["Horseback"])


class Walking(TravellingMethod):
    def __init__(self):
        self.uriRef = URIRef(PATHS["Walking"])
