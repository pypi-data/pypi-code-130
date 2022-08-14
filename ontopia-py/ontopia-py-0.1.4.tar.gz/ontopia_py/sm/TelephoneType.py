from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..l0.Concept import Concept
from ..ns import *

if TYPE_CHECKING:
    from rdflib import Graph

    from .Telephone import Telephone


class TelephoneType(Concept):
    __type__ = SM["TelephoneType"]

    isTelephoneTypeOf: List[Telephone] = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.isTelephoneTypeOf:
            for isTelephoneTypeOf in self.isTelephoneTypeOf:
                g.add(
                    (self.uriRef, SM["isTelephoneTypeOf"], isTelephoneTypeOf.uriRef))
