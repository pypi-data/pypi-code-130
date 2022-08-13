from __future__ import annotations

from typing import TYPE_CHECKING, List, Union

from ..l0.Object import Object
from ..ns import *

if TYPE_CHECKING:
    from rdflib import Graph

    from .CulturalEntity import CulturalEntity
    from .CulturalEvent import CulturalEvent
    from .Site import Site


class CreativeWork(Object):
    __type__ = CIS["CreativeWork"]

    isAbout: List[Union[CulturalEntity, CulturalEvent, Site]] = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.isAbout:
            for isAbout in self.isAbout:
                g.add((self.uriRef, CIS["isAbout"], isAbout.uriRef))
