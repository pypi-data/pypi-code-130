from typing import List

from rdflib import Graph

from ..ns import *
from .Entity import Entity


class Topic(Entity):
    __type__ = L0["Topic"]

    isTopicOf: List[Entity] = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.isTopicOf:
            for isTopicOf in self.isTopicOf:
                g.add((self.uriRef, L0["isTopicOf"],
                       isTopicOf.uriRef))
