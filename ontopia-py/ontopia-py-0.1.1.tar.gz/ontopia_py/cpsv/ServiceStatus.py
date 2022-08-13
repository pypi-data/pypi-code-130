from __future__ import annotations

from typing import TYPE_CHECKING, List

from rdflib import URIRef

from ..l0.Characteristic import Characteristic
from ..ns import *

if TYPE_CHECKING:
    from rdflib import Graph

    from .Service import Service


class ServiceStatus(Characteristic):
    __type__ = CPSV["ServiceStatus"]

    isStatusForService: List[Service] = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.isStatusForService:
            for isStatusForService in self.isStatusForService:
                g.add(
                    (self.uriRef, CPSV["isStatusForService"], isStatusForService.uriRef))


class Active(ServiceStatus):
    def __init__(self):
        self.uriRef = URIRef(CPSV["Active"])


class NonActive(ServiceStatus):
    def __init__(self):
        self.uriRef = URIRef(CPSV["NonActive"])


class UnderDev(ServiceStatus):
    def __init__(self):
        self.uriRef = URIRef(CPSV["UnderDev"])
