from __future__ import annotations

from typing import TYPE_CHECKING

from ..ns import *
from .Person import Person

if TYPE_CHECKING:
    from rdflib import Graph, Literal

from .EducationLevel import EducationLevel


class AlivePerson(Person):
    __type__ = CPV["AlivePerson"]

    hasLevelOfEducation: EducationLevel = None
    age: Literal = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.hasLevelOfEducation:
            g.add((self.uriRef, CPV["hasLevelOfEducation"],
                  self.hasLevelOfEducation.uriRef))

        if self.age:
            g.add((self.uriRef, CPV["age"], self.age))
