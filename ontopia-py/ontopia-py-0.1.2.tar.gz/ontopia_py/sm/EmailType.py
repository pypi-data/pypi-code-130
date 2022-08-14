from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..l0.Concept import Concept
from ..ns import *

if TYPE_CHECKING:
    from rdflib import Graph

    from .Email import Email


class EmailType(Concept):
    __type__ = SM["EmailType"]

    isEmailTypeOf: List[Email] = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.isEmailTypeOf:
            for isEmailTypeOf in self.isEmailTypeOf:
                g.add((self.uriRef, SM["isEmailTypeOf"], isEmailTypeOf.uriRef))
