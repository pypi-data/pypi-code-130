from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..l0.Characteristic import Characteristic
from ..ns import *

if TYPE_CHECKING:
    from rdflib import Graph, Literal


class EducationLevel(Characteristic):
    __type__ = CPV["EducationLevel"]

    educationLevelDesc: List[Literal] = None
    educationLevelID: Literal = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.educationLevelDesc:
            for educationLevelDesc in self.educationLevelDesc:
                g.add(
                    (self.uriRef, CPV["educationLevelDesc"], educationLevelDesc))

        if self.educationLevelID:
            g.add((self.uriRef, CPV["educationLevelID"], self.educationLevelID))
