from __future__ import annotations

from typing import TYPE_CHECKING, List, Union

from ..l0.Description import Description
from ..ns import *

if TYPE_CHECKING:
    from rdflib import Graph, Literal

    from ..cov.Organization import Organization
    from ..cov.PublicOrganizationCategory import PublicOrganizationCategory
    from .TransparencyActivity import TransparencyActivity
    from .TransparencyDataTypology import TransparencyDataTypology
    from .TransparencyObligationStatus import TransparencyObligationStatus
    from .TransparencySubject import TransparencySubject
    from .UpdateFrequency import UpdateFrequency


class TransparencyObligation(Description):
    __type__ = TRANSP["TransparencyObligation"]

    appliesToOrganization: List[Union[Organization,
                                      PublicOrganizationCategory]] = None
    isClassifiedBy: List[TransparencyDataTypology] = None
    hasTransparencyStatus: List[TransparencyObligationStatus] = None
    definesUpdateFrequency: List[UpdateFrequency] = None
    hasTransparencySubject: List[TransparencySubject] = None
    subTransparencyObligationOf: List[TransparencyObligation] = None
    superTransparencyObligationOf: List[TransparencyObligation] = None
    triggers: List[TransparencyActivity] = None
    atTime: List[Literal] = None
    regulationReference: List[Literal] = None
    exceptionObligationNote: List[Literal] = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.appliesToOrganization:
            for appliesToOrganization in self.appliesToOrganization:
                g.add(
                    (self.uriRef, TRANSP["appliesToOrganization"], appliesToOrganization.uriRef))

        if self.isClassifiedBy:
            for isClassifiedBy in self.isClassifiedBy:
                g.add(
                    (self.uriRef, TRANSP["isClassifiedBy"], isClassifiedBy.uriRef))

        if self.hasTransparencyStatus:
            for hasTransparencyStatus in self.hasTransparencyStatus:
                g.add(
                    (self.uriRef, TRANSP["hasTransparencyStatus"], hasTransparencyStatus.uriRef))

        if self.definesUpdateFrequency:
            for definesUpdateFrequency in self.definesUpdateFrequency:
                g.add(
                    (self.uriRef, TRANSP["definesUpdateFrequency"], definesUpdateFrequency.uriRef))

        if self.hasTransparencySubject:
            for hasTransparencySubject in self.hasTransparencySubject:
                g.add(
                    (self.uriRef, TRANSP["hasTransparencySubject"], hasTransparencySubject.uriRef))

        if self.subTransparencyObligationOf:
            for subTransparencyObligationOf in self.subTransparencyObligationOf:
                g.add(
                    (self.uriRef, TRANSP["subTransparencyObligationOf"], subTransparencyObligationOf.uriRef))

        if self.superTransparencyObligationOf:
            for superTransparencyObligationOf in self.superTransparencyObligationOf:
                g.add(
                    (self.uriRef, TRANSP["superTransparencyObligationOf"], superTransparencyObligationOf.uriRef))

        if self.triggers:
            for triggers in self.triggers:
                g.add((self.uriRef, TRANSP["triggers"], triggers.uriRef))

        if self.atTime:
            for atTime in self.atTime:
                g.add((self.uriRef, TI["atTime"], atTime))

        if self.regulationReference:
            for regulationReference in self.regulationReference:
                g.add(
                    (self.uriRef, TRANSP["regulationReference"], regulationReference))

        if self.exceptionObligationNote:
            for exceptionObligationNote in self.exceptionObligationNote:
                g.add(
                    (self.uriRef, TRANSP["exceptionObligationNote"], exceptionObligationNote))
