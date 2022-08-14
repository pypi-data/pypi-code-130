from __future__ import annotations

from typing import TYPE_CHECKING

from ..ns import *
from .Family import Family

if TYPE_CHECKING:
    from rdflib import Graph, Literal


class RegisteredFamily(Family):
    __type__ = CPV["RegisteredFamily"]

    registeredFamilyID: Literal = None
    numberRegFamilyComponents: Literal = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.registeredFamilyID:
            g.add(
                (self.uriRef, CPV["registeredFamilyID"], self.registeredFamilyID))

        if self.numberRegFamilyComponents:
            g.add(
                (self.uriRef, CPV["numberRegFamilyComponents"], self.numberRegFamilyComponents))
