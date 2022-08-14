from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..ns import *
from .Service import Service

if TYPE_CHECKING:
    from rdflib import Graph

    from ..l0.EventOrSituation import EventOrSituation
    from ..language.Language import Language
    from .InteractivityLevel import InteractivityLevel
    from .ServiceSector import ServiceSector
    from .ServiceTheme import ServiceTheme


class PublicService(Service):
    __type__ = CPSV["PublicService"]

    serviceSector: List[ServiceSector] = None
    serviceTheme: List[ServiceTheme] = None
    isPartOfEvent: List[EventOrSituation] = None
    hasLanguage: List[Language] = None
    hasiInteractivityLevel: InteractivityLevel = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.serviceSector:
            for serviceSector in self.serviceSector:
                g.add(
                    (self.uriRef, CPSV["serviceSector"], serviceSector.uriRef))

        if self.serviceTheme:
            for serviceTheme in self.serviceTheme:
                g.add((self.uriRef, CPSV["serviceTheme"], serviceTheme.uriRef))

        if self.isPartOfEvent:
            for isPartOfEvent in self.isPartOfEvent:
                g.add(
                    (self.uriRef, CPSV["isPartOfEvent"], isPartOfEvent.uriRef))

        if self.hasLanguage:
            for hasLanguage in self.hasLanguage:
                g.add((self.uriRef, LANG["hasLanguage"], hasLanguage.uriRef))

        if self.hasiInteractivityLevel:
            g.add((self.uriRef, CPSV["hasiInteractivityLevel"],
                  self.hasiInteractivityLevel.uriRef))
