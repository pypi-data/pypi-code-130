from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..ns import *
from .Person import Person

if TYPE_CHECKING:
    from rdflib import Graph


class FamilySheetHolder(Person):
    __type__ = CPV["FamilySheetHolder"]

    isFamilySheetHolderOf: List[Person] = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.isFamilySheetHolderOf:
            for isFamilySheetHolderOf in self.isFamilySheetHolderOf:
                g.add(
                    (self.uriRef, CPV["isFamilySheetHolderOf"], isFamilySheetHolderOf.uriRef))
