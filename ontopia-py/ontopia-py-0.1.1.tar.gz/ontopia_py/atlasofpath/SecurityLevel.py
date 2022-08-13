from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..l0.Characteristic import Characteristic
from ..ns import *

if TYPE_CHECKING:
    from rdflib import Graph

    from .Pathway import Pathway


class SecurityLevel(Characteristic):
    __type__ = PATHS["SecurityLevel"]

    isSecurityLevelOf: List[Pathway] = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.isSecurityLevelOf:
            for isSecurityLevelOf in self.isSecurityLevelOf:
                g.add(
                    (self.uriRef, PATHS["isSecurityLevelOf"], isSecurityLevelOf.uriRef))
