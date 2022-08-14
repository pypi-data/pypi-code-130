from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..ns import *
from ..l0.Object import Object

if TYPE_CHECKING:
    from rdflib import Graph

    from .Method import Method
    from .Platform import Platform


class MonitoringFacility(Object):
    __type__ = IOT["MonitoringFacility"]

    implementsMethod: List[Method] = None
    isHostedByPlatform: List[Platform] = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.implementsMethod:
            for implementsMethod in self.implementsMethod:
                g.add(
                    (self.uriRef, IOT["implementsMethod"], implementsMethod.uriRef))

        if self.isHostedByPlatform:
            for isHostedByPlatform in self.isHostedByPlatform:
                g.add(
                    (self.uriRef, IOT["isHostedByPlatform"], isHostedByPlatform.uriRef))
