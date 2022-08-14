from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..l0.Object import Object
from ..ns import *

if TYPE_CHECKING:
    from rdflib import Graph

    from .PathStage import PathStage
    from .ServiceType import ServiceType


class SupportService(Object):
    __type__ = PATHS["SupportService"]

    hasServiceType: List[ServiceType] = None
    isSupportServiceOf: List[PathStage] = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.hasServiceType:
            for hasServiceType in self.hasServiceType:
                g.add(
                    (self.uriRef, PATHS["hasServiceType"], hasServiceType.uriRef))

        if self.isSupportServiceOf:
            for isSupportServiceOf in self.isSupportServiceOf:
                g.add(
                    (self.uriRef, PATHS["isSupportServiceOf"], isSupportServiceOf.uriRef))
