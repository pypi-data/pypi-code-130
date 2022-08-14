from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..l0.Agent import Agent
from ..ns import *

if TYPE_CHECKING:
    from rdflib import Graph, Literal

    from ..clv.Address import Address
    from ..l0.Location import Location
    from .Person import Person
    from .PersonTitle import PersonTitle
    from .ResidenceInTime import ResidenceInTime
    from .Sex import Sex


class Person(Agent):
    __type__ = CPV["Person"]

    hasAddress: List[Address] = None
    hasParentalRelationshipWith: List[Person] = None
    isChildOf: List[Person] = None
    isConsortOf: List[Person] = None
    isGrandChildOf: List[Person] = None
    isGrandFatherOf: List[Person] = None
    isNephewOf: List[Person] = None
    isParentOf: List[Person] = None
    isUncleOf: List[Person] = None
    hasPersonTitle: List[PersonTitle] = None
    hasRelationshipWith: List[Person] = None
    knows: List[Person] = None
    hasResidenceInTime: List[ResidenceInTime] = None
    residentIn: List[Address] = None
    hasBirthPlace: Location = None
    hasCitizenship: List[Location] = None
    hasSex: Sex = None
    dateOfBirth: Literal = None
    personID: Literal = None
    altName: Literal = None
    familyName: Literal = None
    givenName: Literal = None
    taxCode: Literal = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.hasAddress:
            for hasAddress in self.hasAddress:
                g.add((self.uriRef, CLV["hasAddress"], hasAddress.uriRef))

        if self.hasParentalRelationshipWith:
            for hasParentalRelationshipWith in self.hasParentalRelationshipWith:
                g.add(
                    (self.uriRef, CPV["hasParentalRelationshipWith"], hasParentalRelationshipWith.uriRef))

        if self.isChildOf:
            for isChildOf in self.isChildOf:
                g.add((self.uriRef, CPV["isChildOf"], isChildOf.uriRef))

        if self.isConsortOf:
            for isConsortOf in self.isConsortOf:
                g.add((self.uriRef, CPV["isConsortOf"], isConsortOf.uriRef))

        if self.isGrandChildOf:
            for isGrandChildOf in self.isGrandChildOf:
                g.add(
                    (self.uriRef, CPV["isGrandChildOf"], isGrandChildOf.uriRef))

        if self.isGrandFatherOf:
            for isGrandFatherOf in self.isGrandFatherOf:
                g.add(
                    (self.uriRef, CPV["isGrandFatherOf"], isGrandFatherOf.uriRef))

        if self.isNephewOf:
            for isNephewOf in self.isNephewOf:
                g.add((self.uriRef, CPV["isNephewOf"], isNephewOf.uriRef))

        if self.isParentOf:
            for isParentOf in self.isParentOf:
                g.add((self.uriRef, CPV["isParentOf"], isParentOf.uriRef))

        if self.isUncleOf:
            for isUncleOf in self.isUncleOf:
                g.add((self.uriRef, CPV["isUncleOf"], isUncleOf.uriRef))

        if self.hasPersonTitle:
            for hasPersonTitle in self.hasPersonTitle:
                g.add(
                    (self.uriRef, CPV["hasPersonTitle"], hasPersonTitle.uriRef))

        if self.hasRelationshipWith:
            for hasRelationshipWith in self.hasRelationshipWith:
                g.add(
                    (self.uriRef, CPV["hasRelationshipWith"], hasRelationshipWith.uriRef))

        if self.knows:
            for knows in self.knows:
                g.add((self.uriRef, CPV["knows"], knows.uriRef))

        if self.hasResidenceInTime:
            for hasResidenceInTime in self.hasResidenceInTime:
                g.add(
                    (self.uriRef, CPV["hasResidenceInTime"], hasResidenceInTime.uriRef))

        if self.residentIn:
            for residentIn in self.residentIn:
                g.add((self.uriRef, CPV["residentIn"], residentIn.uriRef))

        if self.hasCitizenship:
            for hasCitizenship in self.hasCitizenship:
                g.add(
                    (self.uriRef, CPV["hasCitizenship"], hasCitizenship.uriRef))

        if self.hasBirthPlace:
            g.add((self.uriRef, CPV["hasBirthPlace"], self.hasBirthPlace.uriRef))

        if self.dateOfBirth:
            g.add((self.uriRef, CPV["dateOfBirth"], self.dateOfBirth))

        if self.personID:
            g.add((self.uriRef, CPV["personID"], self.personID))

        if self.altName:
            g.add((self.uriRef, CPV["altName"], self.altName))

        if self.familyName:
            g.add((self.uriRef, CPV["familyName"], self.familyName))

        if self.givenName:
            g.add((self.uriRef, CPV["givenName"], self.givenName))

        if self.taxCode:
            g.add((self.uriRef, CPV["taxCode"], self.taxCode))
