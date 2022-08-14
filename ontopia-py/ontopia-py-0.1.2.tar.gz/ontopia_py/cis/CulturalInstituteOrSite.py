from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..ns import *
from ..poi.PointOfInterest import PointOfInterest
from .CulturalEntity import CulturalEntity

if TYPE_CHECKING:
    from rdflib import Graph, Literal

    from ..accesscondition.AccessCondition import AccessCondition
    from ..clv.Feature import Feature
    from ..pot.Ticket import Ticket
    from ..ro.TimeIndexedRole import TimeIndexedRole
    from ..sm.OnlineContactPoint import OnlineContactPoint
    from .Catalogue import Catalogue
    from .CISNameInTime import CISNameInTime
    from .CISService import CISService
    from .CISType import CISType
    from .CollectionCulEnt import CollectionCulEnt
    from .CreativeWork import CreativeWork
    from .CulturalProject import CulturalProject
    from .Equipment import Equipment
    from .Site import Site
    from .SubjectDiscipline import SubjectDiscipline


class CulturalInstituteOrSite(CulturalEntity, PointOfInterest):
    __type__ = CIS["CulturalInstituteOrSite"]

    hasCISType: List[CISType] = None
    hasSite: List[Site] = None
    hasRiT: List[TimeIndexedRole] = None
    catalogue: List[Catalogue] = None
    hasCISNameInTime: List[CISNameInTime] = None
    hasCollection: List[CollectionCulEnt] = None
    hasDiscipline: List[SubjectDiscipline] = None
    isInvolvedInProject: List[CulturalProject] = None
    isPartOf: List[CulturalInstituteOrSite] = None
    isSubjectOf: List[CreativeWork] = None
    makesAvailableEquipment: List[Equipment] = None
    providesService: List[CISService] = None
    hasAccessCondition: List[AccessCondition] = None
    hasOnlineContactPoint: List[OnlineContactPoint] = None
    hasSpatialCoverage: List[Feature] = None
    hasTicket: List[Ticket] = None
    institutionalCISName: List[Literal] = None
    description: List[Literal] = None
    ISILIdentifier: Literal = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.hasCISType:
            for hasCISType in self.hasCISType:
                g.add((self.uriRef, CIS["hasCISType"], hasCISType.uriRef))

        if self.hasSite:
            for hasSite in self.hasSite:
                g.add((self.uriRef, CIS["hasSite"], hasSite.uriRef))

        if self.hasRiT:
            for hasRiT in self.hasRiT:
                g.add((self.uriRef, RO["hasRiT"], hasRiT.uriRef))

        if self.catalogue:
            for catalogue in self.catalogue:
                g.add((self.uriRef, CIS["catalogue"], catalogue.uriRef))

        if self.hasCISNameInTime:
            for hasCISNameInTime in self.hasCISNameInTime:
                g.add(
                    (self.uriRef, CIS["hasCISNameInTime"], hasCISNameInTime.uriRef))

        if self.hasCollection:
            for hasCollection in self.hasCollection:
                g.add(
                    (self.uriRef, CIS["hasCollection"], hasCollection.uriRef))

        if self.hasDiscipline:
            for hasDiscipline in self.hasDiscipline:
                g.add(
                    (self.uriRef, CIS["hasDiscipline"], hasDiscipline.uriRef))

        if self.isInvolvedInProject:
            for isInvolvedInProject in self.isInvolvedInProject:
                g.add(
                    (self.uriRef, CIS["isInvolvedInProject"], isInvolvedInProject.uriRef))

        if self.isPartOf:
            for isPartOf in self.isPartOf:
                g.add((self.uriRef, CIS["isPartOf"], isPartOf.uriRef))

        if self.isSubjectOf:
            for isSubjectOf in self.isSubjectOf:
                g.add((self.uriRef, CIS["isSubjectOf"], isSubjectOf.uriRef))

        if self.makesAvailableEquipment:
            for makesAvailableEquipment in self.makesAvailableEquipment:
                g.add(
                    (self.uriRef, CIS["makesAvailableEquipment"], makesAvailableEquipment.uriRef))

        if self.providesService:
            for providesService in self.providesService:
                g.add(
                    (self.uriRef, CIS["providesService"], providesService.uriRef))

        if self.hasAccessCondition:
            for hasAccessCondition in self.hasAccessCondition:
                g.add(
                    (self.uriRef, ACOND["hasAccessCondition"], hasAccessCondition.uriRef))

        if self.hasOnlineContactPoint:
            for hasOnlineContactPoint in self.hasOnlineContactPoint:
                g.add(
                    (self.uriRef, SM["hasOnlineContactPoint"], hasOnlineContactPoint.uriRef))

        if self.hasSpatialCoverage:
            for hasSpatialCoverage in self.hasSpatialCoverage:
                g.add(
                    (self.uriRef, CLV["hasSpatialCoverage"], hasSpatialCoverage.uriRef))

        if self.hasTicket:
            for hasTicket in self.hasTicket:
                g.add((self.uriRef, POT["hasTicket"], hasTicket.uriRef))

        if self.institutionalCISName:
            for institutionalCISName in self.institutionalCISName:
                g.add(
                    (self.uriRef, CIS["institutionalCISName"], institutionalCISName))

        if self.description:
            for description in self.description:
                g.add((self.uriRef, L0["description"], description))

        if self.ISILIdentifier:
            g.add((self.uriRef, CIS["ISILIdentifier"], self.ISILIdentifier))
