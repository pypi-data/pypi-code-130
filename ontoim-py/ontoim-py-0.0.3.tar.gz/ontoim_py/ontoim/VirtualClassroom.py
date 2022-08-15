from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..ns import *
from .Classroom import Classroom

if TYPE_CHECKING:
    from rdflib import Graph

    from .VideoCommunicationService import VideoCommunicationService


class VirtualClassroom(Classroom):
    __type__ = ONTOIM["VirtualClassroom"]

    usesVideoCommunicationService: List[VideoCommunicationService] = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.usesVideoCommunicationService:
            for usesVideoCommunicationService in self.usesVideoCommunicationService:
                g.add(
                    (self.uriRef, ONTOIM["usesVideoCommunicationService"], usesVideoCommunicationService.uriRef))
