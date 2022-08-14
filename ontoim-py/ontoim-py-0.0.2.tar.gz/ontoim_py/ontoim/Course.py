from __future__ import annotations

from typing import TYPE_CHECKING, List

from ontopia_py.her.AcademicDiscipline import AcademicDiscipline
from ontopia_py.l0.Activity import Activity

from ..ns import *

if TYPE_CHECKING:
    from ontopia_py.pot.PriceSpecification import PriceSpecification
    from ontopia_py.ti.TimeInterval import TimeInterval
    from rdflib import Graph, Literal

    from .Classroom import Classroom
    from .Subscriber import Subscriber
    from .Subscribers import Subscribers


class Course(Activity):
    __type__ = ONTOIM["Course"]

    atTime: List[TimeInterval] = None
    hasPriceSpecification: List[PriceSpecification] = None
    hasSubscribers: List[Subscribers] = None
    hasSubscription: List[Subscriber] = None
    situatedInClassroom: List[Classroom] = None
    name: List[Literal] = None
    description: List[Literal] = None
    courseCode: Literal = None
    durationHours: Literal = None
    hasAcademicDiscipline: List[AcademicDiscipline] = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.atTime:
            for atTime in self.atTime:
                g.add((self.uriRef, TI["atTime"], atTime.uriRef))

        if self.hasPriceSpecification:
            for hasPriceSpecification in self.hasPriceSpecification:
                g.add(
                    (self.uriRef, ONTOIM["hasPriceSpecification"], hasPriceSpecification.uriRef))

        if self.hasSubscribers:
            for hasSubscribers in self.hasSubscribers:
                g.add(
                    (self.uriRef, ONTOIM["hasSubscribers"], hasSubscribers.uriRef))

        if self.hasSubscription:
            for hasSubscription in self.hasSubscription:
                g.add(
                    (self.uriRef, ONTOIM["hasSubscription"], hasSubscription.uriRef))

        if self.situatedInClassroom:
            for situatedInClassroom in self.situatedInClassroom:
                g.add(
                    (self.uriRef, ONTOIM["situatedInClassroom"], situatedInClassroom.uriRef))
        
        if self.hasAcademicDiscipline:
            for hasAcademicDiscipline in self.hasAcademicDiscipline:
                g.add(
                    (self.uriRef, HER["hasAcademicDiscipline"], hasAcademicDiscipline.uriRef))

        if self.name:
            for name in self.name:
                g.add((self.uriRef, L0["name"], name))

        if self.description:
            for description in self.description:
                g.add((self.uriRef, L0["description"], description))

        if self.courseCode:
            g.add((self.uriRef, ONTOIM["courseCode"], self.courseCode))

        if self.durationHours:
            g.add((self.uriRef, ONTOIM["durationHours"], self.durationHours))
