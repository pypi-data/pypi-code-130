from __future__ import annotations

from typing import TYPE_CHECKING, List

from ontopia_py.l0.Object import Object

from ..ns import *

if TYPE_CHECKING:
    from ontopia_py.clv.Country import Country
    from ontopia_py.mu.Value import Value
    from rdflib import Graph, Literal

    from .VehicleCategory import VehicleCategory


class Vehicle(Object):
    __type__ = ONTOIM["Vehicle"]

    hasEngineDisplacement: List[Value] = None
    hasHeight: List[Value] = None
    hasLength: List[Value] = None
    hasWeight: List[Value] = None
    hasWidth: List[Value] = None
    hasVehicleCategory: VehicleCategory = None
    hasRegistrationCountry: Country = None
    brand: List[Literal] = None
    color: List[Literal] = None
    model: List[Literal] = None
    licensePlate: Literal = None
    registrationYear: Literal = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.hasEngineDisplacement:
            for hasEngineDisplacement in self.hasEngineDisplacement:
                g.add(
                    (self.uriRef, ONTOIM["hasEngineDisplacement"], hasEngineDisplacement.uriRef))

        if self.hasHeight:
            for hasHeight in self.hasHeight:
                g.add((self.uriRef, ONTOIM["hasHeight"], hasHeight.uriRef))

        if self.hasLength:
            for hasLength in self.hasLength:
                g.add((self.uriRef, ONTOIM["hasLength"], hasLength.uriRef))

        if self.hasWeight:
            for hasWeight in self.hasWeight:
                g.add((self.uriRef, ONTOIM["hasWeight"], hasWeight.uriRef))

        if self.hasWidth:
            for hasWidth in self.hasWidth:
                g.add((self.uriRef, ONTOIM["hasWidth"], hasWidth.uriRef))

        if self.hasVehicleCategory:
            g.add(
                (self.uriRef, ONTOIM["hasVehicleCategory"], self.hasVehicleCategory.uriRef))

        if self.hasRegistrationCountry:
            g.add(
                (self.uriRef, ONTOIM["hasRegistrationCountry"], self.hasRegistrationCountry.uriRef))

        if self.brand:
            for brand in self.brand:
                g.add((self.uriRef, ONTOIM["brand"], brand))

        if self.color:
            for color in self.color:
                g.add((self.uriRef, ONTOIM["color"], color))

        if self.model:
            for model in self.model:
                g.add((self.uriRef, ONTOIM["model"], model))

        if self.licensePlate:
            g.add((self.uriRef, ONTOIM["licensePlate"], self.licensePlate))

        if self.registrationYear:
            g.add(
                (self.uriRef, ONTOIM["registrationYear"], self.registrationYear))
