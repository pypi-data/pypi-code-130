from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..l0.Object import Object
from ..ns import *

if TYPE_CHECKING:
    from rdflib import Graph, Literal

    from ..clv.Feature import Feature
    from ..ro.TimeIndexedRole import TimeIndexedRole
    from ..sm.OnlineContactPoint import OnlineContactPoint
    from ..ti.TemporalEntity import TemporalEntity
    from .Authentication import Authentication
    from .Channel import Channel
    from .Cost import Cost
    from .EmailChannel import EmailChannel
    from .Input import Input
    from .OtherElectronicChannel import OtherElectronicChannel
    from .Output import Output
    from .PhoneChannel import PhoneChannel
    from .Rule import Rule
    from .ServiceProcessingTime import ServiceProcessingTime
    from .ServiceStatus import ServiceStatus
    from .WebSiteChannel import WebSiteChannel


class Service(Object):
    __type__ = CPSV["Service"]

    hasAuthenticationMethod: List[Authentication] = None
    hasChannel: List[Channel] = None
    hasRiT: List[TimeIndexedRole] = None
    hasSpatialCoverage: List[Feature] = None
    hasCost: List[Cost] = None
    hasInput: List[Input] = None
    isCompliantWithRule: List[Rule] = None
    isPhysicallyAvailableAt: List[Feature] = None
    producesOutput: List[Output] = None
    relationService: List[Service] = None
    requiresService: List[Service] = None
    hasOnlineContactPoint: List[OnlineContactPoint] = None
    hasTemporalCoverage: List[TemporalEntity] = None
    hasProcessingTime: List[ServiceProcessingTime] = None
    hasWebSiteCh: List[WebSiteChannel] = None
    hasEmailCh: List[EmailChannel] = None
    hasOtherElectronicCh: List[OtherElectronicChannel] = None
    hasPhoneCh: List[PhoneChannel] = None
    hasServiceStatus: ServiceStatus = None
    description: List[Literal] = None
    name: List[Literal] = None
    otherServiceCode: List[Literal] = None
    serviceKeyword: List[Literal] = None
    identifier: Literal = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.hasAuthenticationMethod:
            for hasAuthenticationMethod in self.hasAuthenticationMethod:
                g.add(
                    (self.uriRef, CPSV["hasAuthenticationMethod"], hasAuthenticationMethod.uriRef))

        if self.hasChannel:
            for hasChannel in self.hasChannel:
                g.add((self.uriRef, CPSV["hasChannel"], hasChannel.uriRef))

        if self.hasRiT:
            for hasRiT in self.hasRiT:
                g.add((self.uriRef, RO["hasRiT"], hasRiT.uriRef))

        if self.hasSpatialCoverage:
            for hasSpatialCoverage in self.hasSpatialCoverage:
                g.add(
                    (self.uriRef, CLV["hasSpatialCoverage"], hasSpatialCoverage.uriRef))

        if self.hasCost:
            for hasCost in self.hasCost:
                g.add((self.uriRef, CPSV["hasCost"], hasCost.uriRef))

        if self.hasInput:
            for hasInput in self.hasInput:
                g.add((self.uriRef, CPSV["hasInput"], hasInput.uriRef))

        if self.isCompliantWithRule:
            for isCompliantWithRule in self.isCompliantWithRule:
                g.add(
                    (self.uriRef, CPSV["isCompliantWithRule"], isCompliantWithRule.uriRef))

        if self.isPhysicallyAvailableAt:
            for isPhysicallyAvailableAt in self.isPhysicallyAvailableAt:
                g.add(
                    (self.uriRef, CPSV["isPhysicallyAvailableAt"], isPhysicallyAvailableAt.uriRef))

        if self.producesOutput:
            for producesOutput in self.producesOutput:
                g.add(
                    (self.uriRef, CPSV["producesOutput"], producesOutput.uriRef))

        if self.relationService:
            for relationService in self.relationService:
                g.add(
                    (self.uriRef, CPSV["relationService"], relationService.uriRef))

        if self.requiresService:
            for requiresService in self.requiresService:
                g.add(
                    (self.uriRef, CPSV["requiresService"], requiresService.uriRef))

        if self.hasOnlineContactPoint:
            for hasOnlineContactPoint in self.hasOnlineContactPoint:
                g.add(
                    (self.uriRef, SM["hasOnlineContactPoint"], hasOnlineContactPoint.uriRef))

        if self.hasTemporalCoverage:
            for hasTemporalCoverage in self.hasTemporalCoverage:
                g.add(
                    (self.uriRef, TI["hasTemporalCoverage"], hasTemporalCoverage.uriRef))

        if self.hasProcessingTime:
            for hasProcessingTime in self.hasProcessingTime:
                g.add(
                    (self.uriRef, CPSV["hasProcessingTime"], hasProcessingTime.uriRef))

        if self.hasWebSiteCh:
            for hasWebSiteCh in self.hasWebSiteCh:
                g.add((self.uriRef, CPSV["hasWebSiteCh"], hasWebSiteCh.uriRef))

        if self.hasEmailCh:
            for hasEmailCh in self.hasEmailCh:
                g.add((self.uriRef, CPSV["hasEmailCh"], hasEmailCh.uriRef))

        if self.hasOtherElectronicCh:
            for hasOtherElectronicCh in self.hasOtherElectronicCh:
                g.add(
                    (self.uriRef, CPSV["hasOtherElectronicCh"], hasOtherElectronicCh.uriRef))

        if self.hasPhoneCh:
            for hasPhoneCh in self.hasPhoneCh:
                g.add((self.uriRef, CPSV["hasPhoneCh"], hasPhoneCh.uriRef))

        if self.hasServiceStatus:
            g.add((self.uriRef, CPSV["hasServiceStatus"],
                  self.hasServiceStatus.uriRef))

        if self.description:
            for description in self.description:
                g.add((self.uriRef, L0["description"], description))

        if self.name:
            for name in self.name:
                g.add((self.uriRef, L0["name"], name))

        if self.otherServiceCode:
            for otherServiceCode in self.otherServiceCode:
                g.add(
                    (self.uriRef, CPSV["otherServiceCode"], otherServiceCode))

        if self.serviceKeyword:
            for serviceKeyword in self.serviceKeyword:
                g.add((self.uriRef, CPSV["serviceKeyword"], serviceKeyword))

        if self.identifier:
            g.add((self.uriRef, L0["identifier"], self.identifier))
