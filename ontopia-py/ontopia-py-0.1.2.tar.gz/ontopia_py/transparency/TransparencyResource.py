from __future__ import annotations

from typing import TYPE_CHECKING, List, Union

from ..l0.Object import Object
from ..ns import *

if TYPE_CHECKING:
    from rdflib import Graph, Literal

    from ..l0.Activity import Activity
    from .Format import Format
    from .TransparencyActivity import TransparencyActivity
    from .UpdateFrequency import UpdateFrequency


class TransparencyResource(Object):
    __type__ = TRANSP["TransparencyResource"]

    refersToTransparencyEntity: List[Union[Activity, Object]] = None
    generatedBy: List[TransparencyActivity] = None
    hasAllowedFormat: List[Format] = None
    mustBeUptodatedWithin: List[UpdateFrequency] = None
    generatedBy: List[TransparencyActivity] = None
    isVersionOf: List[TransparencyResource] = None
    name: List[Literal] = None
    downloadURL: List[Literal] = None
    accessURL: Literal = None
    modified: Literal = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.refersToTransparencyEntity:
            for refersToTransparencyEntity in self.refersToTransparencyEntity:
                g.add(
                    (self.uriRef, TRANSP["refersToTransparencyEntity"], refersToTransparencyEntity.uriRef))

        if self.generatedBy:
            for generatedBy in self.generatedBy:
                g.add((self.uriRef, TRANSP["generatedBy"], generatedBy.uriRef))

        if self.hasAllowedFormat:
            for hasAllowedFormat in self.hasAllowedFormat:
                g.add(
                    (self.uriRef, TRANSP["hasAllowedFormat"], hasAllowedFormat.uriRef))

        if self.mustBeUptodatedWithin:
            for mustBeUptodatedWithin in self.mustBeUptodatedWithin:
                g.add(
                    (self.uriRef, TRANSP["mustBeUptodatedWithin"], mustBeUptodatedWithin.uriRef))

        if self.generatedBy:
            for generatedBy in self.generatedBy:
                g.add((self.uriRef, TRANSP["generatedBy"], generatedBy.uriRef))

        if self.isVersionOf:
            for isVersionOf in self.isVersionOf:
                g.add((self.uriRef, TRANSP["isVersionOf"], isVersionOf.uriRef))

        if self.name:
            for name in self.name:
                g.add((self.uriRef, TRANSP["name"], name))

        if self.downloadURL:
            for downloadURL in self.downloadURL:
                g.add((self.uriRef, TRANSP["downloadURL"], downloadURL))

        if self.accessURL:
            g.add((self.uriRef, TRANSP["accessURL"], self.accessURL))

        if self.modified:
            g.add((self.uriRef, TRANSP["modified"], self.modified))
