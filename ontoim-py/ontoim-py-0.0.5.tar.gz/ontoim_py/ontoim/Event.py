from __future__ import annotations

from typing import TYPE_CHECKING, List

from ontopia_py.cpev.Event import Event

from ..ns import *

if TYPE_CHECKING:
    from ontopia_py.cov.Organization import Organization
    from rdflib import Graph

    from .Subscriber import Subscriber
    from .Subscribers import Subscribers


class Event(Event):
    __type__ = ONTOIM["Event"]

    hasSubscription: List[Subscriber] = None
    hasSubscribers: List[Subscribers] = None
    isOrganizedBy: List[Organization] = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.hasSubscription:
            for hasSubscription in self.hasSubscription:
                g.add(
                    (self.uriRef, ONTOIM["hasSubscription"], hasSubscription.uriRef))

        if self.hasSubscribers:
            for hasSubscribers in self.hasSubscribers:
                g.add(
                    (self.uriRef, ONTOIM["hasSubscribers"], hasSubscribers.uriRef))
        
        if self.isOrganizedBy:
            for isOrganizedBy in self.isOrganizedBy:
                g.add(
                    (self.uriRef, ONTOIM["isOrganizedBy"], isOrganizedBy.uriRef))
