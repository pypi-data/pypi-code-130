from __future__ import annotations

from typing import TYPE_CHECKING, List

from ontopia_py.l0.Collection import Collection

from ..ns import *

if TYPE_CHECKING:
    from rdflib import Graph

    from .Facility import Facility
    from .HeritageType import HeritageType


class Heritage(Collection):
    __type__ = ONTOIM["Heritage"]

    hasFacility: List[Facility] = None
    hasHeritageType: List[HeritageType] = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.hasFacility:
            for hasFacility in self.hasFacility:
                g.add((self.uriRef, ONTOIM["hasFacility"], hasFacility.uriRef))

        if self.hasHeritageType:
            g.add(
                (self.uriRef, ONTOIM["hasHeritageType"], self.hasHeritageType.uriRef))
