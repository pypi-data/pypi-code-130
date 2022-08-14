from __future__ import annotations

from typing import TYPE_CHECKING, List

from ontopia_py.poi.PointOfInterest import PointOfInterest

from ..ns import *

if TYPE_CHECKING:
    from ontopia_py.acco.OSDFeature import OSDFeature
    from ontopia_py.cov.Organization import Organization
    from ontopia_py.publiccontract.Procedure import Procedure
    from ontopia_py.sm.OnlineContactPoint import OnlineContactPoint
    from ontopia_py.sm.PhysicalContactPoint import PhysicalContactPoint
    from rdflib import Graph

    from .CadastralData import CadastralData


class Facility(PointOfInterest):
    __type__ = ONTOIM["Facility"]

    hasOfferedService: List[OSDFeature] = None
    concessedWithProcedure: List[Procedure] = None
    ownedBy: List[Organization] = None
    hasCadastralData: CadastralData = None
    hasOnlineContactPoint: OnlineContactPoint = None
    hasPhysicalContactPoint: PhysicalContactPoint = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.hasOfferedService:
            for hasOfferedService in self.hasOfferedService:
                g.add(
                    (self.uriRef, ONTOIM["hasOfferedService"], hasOfferedService.uriRef))

        if self.concessedWithProcedure:
            for concessedWithProcedure in self.concessedWithProcedure:
                g.add(
                    (self.uriRef, ONTOIM["concessedWithProcedure"], concessedWithProcedure.uriRef))

        if self.ownedBy:
            for ownedBy in self.ownedBy:
                g.add((self.uriRef, ONTOIM["ownedBy"], ownedBy.uriRef))

        if self.hasCadastralData:
            g.add(
                (self.uriRef, ONTOIM["hasCadastralData"], self.hasCadastralData.uriRef))

        if self.hasOnlineContactPoint:
            g.add(
                (self.uriRef, SM["hasOnlineContactPoint"], self.hasOnlineContactPoint.uriRef))

        if self.hasPhysicalContactPoint:
            g.add(
                (self.uriRef, SM["hasPhysicalContactPoint"], self.hasPhysicalContactPoint.uriRef))
