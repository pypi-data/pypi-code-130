from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..l0.Description import Description
from ..ns import *

if TYPE_CHECKING:
    from rdflib import Graph

    from .RegisteredFamily import RegisteredFamily


class ParentalRelationshipType(Description):
    __type__ = CPV["ParentalRelationshipType"]

    inRegisteredFamily: List[RegisteredFamily] = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.inRegisteredFamily:
            for inRegisteredFamily in self.inRegisteredFamily:
                g.add(
                    (self.uriRef, CPV["inRegisteredFamily"], inRegisteredFamily.uriRef))
