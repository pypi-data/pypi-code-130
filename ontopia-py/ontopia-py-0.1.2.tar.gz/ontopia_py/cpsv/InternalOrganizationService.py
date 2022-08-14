from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..ns import *
from .Service import Service

if TYPE_CHECKING:
    from rdflib import Graph, Literal


class InternalOrganizationService(Service):
    __type__ = CPSV["InternalOrganizationService"]

    additionalNoteForService: List[Literal] = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.additionalNoteForService:
            for additionalNoteForService in self.additionalNoteForService:
                g.add(
                    (self.uriRef, CPSV["additionalNoteForService"], additionalNoteForService))
