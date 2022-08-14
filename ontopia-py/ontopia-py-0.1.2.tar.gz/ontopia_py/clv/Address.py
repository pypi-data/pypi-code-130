from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..ns import *
from .Feature import Feature

if TYPE_CHECKING:
    from rdflib import Graph, Literal

    from .AddressArea import AddressArea
    from .AddressComponent import AddressComponent
    from .AddressInTime import AddressInTime
    from .CensusSection import CensusSection
    from .City import City
    from .CivicNumbering import CivicNumbering
    from .Country import Country
    from .District import District
    from .InternalAccess import InternalAccess
    from .Province import Province
    from .Region import Region
    from .StreetToponym import StreetToponym


class Address(Feature):
    __type__ = CLV["Address"]

    hasAddressComponent: List[AddressComponent] = None
    hasInternalAccess: List[InternalAccess] = None
    hasNumber: CivicNumbering = None
    hasStreetToponym: StreetToponym = None
    hasAdressinTime: AddressInTime = None
    hasCensusSection: CensusSection = None
    fullAddress: Literal = None
    postCode: Literal = None
    hasAddressArea: List[AddressArea] = None
    hasCity: List[City] = None
    hasCountry: List[Country] = None
    hasDistrict: List[District] = None
    hasProvince: List[Province] = None
    hasRegion: List[Region] = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.hasAddressComponent:
            for hasAddressComponent in self.hasAddressComponent:
                g.add(
                    (self.uriRef, CLV["hasAddressComponent"], hasAddressComponent.uriRef))

        if self.hasInternalAccess:
            for hasInternalAccess in self.hasInternalAccess:
                g.add(
                    (self.uriRef, CLV["hasInternalAccess"], hasInternalAccess.uriRef))

        if self.hasNumber:
            g.add((self.uriRef, CLV["hasNumber"], self.hasNumber.uriRef))

        if self.hasStreetToponym:
            g.add((self.uriRef, CLV["hasStreetToponym"],
                  self.hasStreetToponym.uriRef))

        if self.hasAdressinTime:
            g.add((self.uriRef, CLV["hasAdressinTime"],
                  self.hasAdressinTime.uriRef))

        if self.hasCensusSection:
            g.add((self.uriRef, CLV["hasCensusSection"],
                  self.hasCensusSection.uriRef))

        if self.fullAddress:
            g.add((self.uriRef, CLV["fullAddress"], self.fullAddress))

        if self.postCode:
            g.add((self.uriRef, CLV["postCode"], self.postCode))

        if self.hasAddressArea:
            for hasAddressArea in self.hasAddressArea:
                g.add(
                    (self.uriRef, CLV["hasAddressArea"], hasAddressArea.uriRef))

        if self.hasCity:
            for hasCity in self.hasCity:
                g.add(
                    (self.uriRef, CLV["hasCity"], hasCity.uriRef))

        if self.hasCountry:
            for hasCountry in self.hasCountry:
                g.add(
                    (self.uriRef, CLV["hasCountry"], hasCountry.uriRef))

        if self.hasDistrict:
            for hasDistrict in self.hasDistrict:
                g.add(
                    (self.uriRef, CLV["hasDistrict"], hasDistrict.uriRef))

        if self.hasProvince:
            for hasProvince in self.hasProvince:
                g.add(
                    (self.uriRef, CLV["hasProvince"], hasProvince.uriRef))

        if self.hasRegion:
            for hasRegion in self.hasRegion:
                g.add(
                    (self.uriRef, CLV["hasRegion"], hasRegion.uriRef))