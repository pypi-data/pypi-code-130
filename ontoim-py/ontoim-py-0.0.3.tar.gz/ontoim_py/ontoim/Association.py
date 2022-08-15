from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..ns import *
from .PrivateOrganization import PrivateOrganization

if TYPE_CHECKING:
    from ontopia_py.cpv.Person import Person
    from rdflib import Graph, Literal

    from .AssociationCategory import AssociationCategory
    from .Members import Members
    from .Subscriber import Subscriber


class Association(PrivateOrganization):
    __type__ = ONTOIM["Association"]

    hasAssociationCategory: List[AssociationCategory] = None
    hasMembers: List[Members] = None
    hasReferent: List[Person] = None
    hasSubscription: List[Subscriber] = None
    associationRegisterCode: Literal = None
    associationRegistrationDate: Literal = None
    associationRemovalFromRegisterDate: Literal = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.hasAssociationCategory:
            for hasAssociationCategory in self.hasAssociationCategory:
                g.add(
                    (self.uriRef, ONTOIM["hasAssociationCategory"], hasAssociationCategory.uriRef))

        if self.hasMembers:
            for hasMembers in self.hasMembers:
                g.add(
                    (self.uriRef, ONTOIM["hasMembers"], hasMembers.uriRef))

        if self.hasReferent:
            for hasReferent in self.hasReferent:
                g.add(
                    (self.uriRef, ONTOIM["hasReferent"], hasReferent.uriRef))

        if self.hasSubscription:
            for hasSubscription in self.hasSubscription:
                g.add(
                    (self.uriRef, ONTOIM["hasSubscription"], hasSubscription.uriRef))

        if self.associationRegisterCode:
            g.add(
                (self.uriRef, ONTOIM["associationRegisterCode"], self.associationRegisterCode))

        if self.associationRegistrationDate:
            g.add(
                (self.uriRef, ONTOIM["associationRegistrationDate"], self.associationRegistrationDate))

        if self.associationRemovalFromRegisterDate:
            g.add(
                (self.uriRef, ONTOIM["associationRemovalFromRegisterDate"], self.associationRemovalFromRegisterDate))
