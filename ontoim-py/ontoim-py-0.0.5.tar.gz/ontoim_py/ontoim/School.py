from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..ns import *
from .Facility import Facility

if TYPE_CHECKING:
    from rdflib import Graph, Literal

    from .Course import Course
    from .SchoolType import SchoolType
    from .Subscriber import Subscriber
    from .Subscribers import Subscribers


class School(Facility):
    __type__ = ONTOIM["School"]

    hasSchoolType: List[SchoolType] = None
    hasSubscribers: List[Subscribers] = None
    hasSubscription: List[Subscriber] = None
    providesCourse: List[Course] = None
    schoolCode: Literal = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.hasSchoolType:
            for hasSchoolType in self.hasSchoolType:
                g.add(
                    (self.uriRef, ONTOIM["hasSchoolType"], hasSchoolType.uriRef))

        if self.hasSubscribers:
            for hasSubscribers in self.hasSubscribers:
                g.add(
                    (self.uriRef, ONTOIM["hasSubscribers"], hasSubscribers.uriRef))

        if self.hasSubscription:
            for hasSubscription in self.hasSubscription:
                g.add(
                    (self.uriRef, ONTOIM["hasSubscription"], hasSubscription.uriRef))

        if self.providesCourse:
            for providesCourse in self.providesCourse:
                g.add(
                    (self.uriRef, ONTOIM["providesCourse"], providesCourse.uriRef))

        if self.schoolCode:
            g.add((self.uriRef, ONTOIM["schoolCode"], self.schoolCode))
