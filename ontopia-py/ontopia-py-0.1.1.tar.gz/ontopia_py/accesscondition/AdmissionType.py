from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..l0.Characteristic import Characteristic
from ..ns import *

if TYPE_CHECKING:
    from rdflib import Graph, Literal

    from ..Thing import Thing


class AdmissionType(Characteristic):
    __type__ = ACOND["AdmissionType"]

    name: List[Literal] = None
    description: List[Literal] = None
    isAdmissionTypeOf: List[Thing]

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.isAdmissionTypeOf:
            for isAdmissionTypeOf in self.isAdmissionTypeOf:
                g.add(
                    (self.uriRef, ACOND["isAdmissionTypeOf"], isAdmissionTypeOf.uriRef))

        if self.name:
            for name in self.name:
                g.add((self.uriRef, L0["name"], name))

        if self.description:
            for description in self.description:
                g.add((self.uriRef, L0["description"], description))
