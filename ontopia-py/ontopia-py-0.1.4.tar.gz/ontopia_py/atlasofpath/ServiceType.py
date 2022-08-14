from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..l0.Concept import Concept
from ..ns import *

if TYPE_CHECKING:
    from rdflib import Graph

    from .SupportService import SupportService


class ServiceType(Concept):
    __type__ = PATHS["ServiceType"]

    isServiceTypeOf: List[SupportService] = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.isServiceTypeOf:
            for isServiceTypeOf in self.isServiceTypeOf:
                g.add(
                    (self.uriRef, PATHS["isServiceTypeOf"], isServiceTypeOf.uriRef))
