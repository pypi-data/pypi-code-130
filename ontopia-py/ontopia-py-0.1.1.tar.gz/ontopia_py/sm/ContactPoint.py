from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..l0.Object import Object
from ..ns import *

if TYPE_CHECKING:
    from rdflib import Graph

    from ..accesscondition.AccessCondition import AccessCondition


class ContactPoint(Object):
    __type__ = SM["ContactPoint"]

    available: List[AccessCondition] = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.available:
            for available in self.available:
                g.add((self.uriRef, SM["available"], available.uriRef))
