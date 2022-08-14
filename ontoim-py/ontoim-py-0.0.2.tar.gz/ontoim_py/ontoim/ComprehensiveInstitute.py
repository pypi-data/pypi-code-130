from __future__ import annotations

from typing import TYPE_CHECKING, List

from ontopia_py.poi.MultiplePointOfInterest import MultiplePointOfInterest

from ..ns import *
from .School import School

if TYPE_CHECKING:
    from rdflib import Graph


class ComprehensiveInstitute(School, MultiplePointOfInterest):
    __type__ = ONTOIM["ComprehensiveInstitute"]

    includesSchool: List[School] = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.includesSchool:
            for includesSchool in self.includesSchool:
                g.add(
                    (self.uriRef, ONTOIM["includesSchool"], includesSchool.uriRef))
