from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..ns import *
from .AmendmentDocument import AmendmentDocument

if TYPE_CHECKING:
    from rdflib import Graph, Literal

    from .VariantReason import VariantReason


class VariantDocument(AmendmentDocument):
    __type__ = PUBC["VariantDocument"]

    variantReason: List[VariantReason] = None
    additionalDay: List[Literal] = None
    increaseAmount: List[Literal] = None
    reductionAmount: List[Literal] = None
    variantDate: List[Literal] = None
    variantType: List[Literal] = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.variantReason:
            for variantReason in self.variantReason:
                g.add(
                    (self.uriRef, PUBC["variantReason"], variantReason.uriRef))

        if self.additionalDay:
            for additionalDay in self.additionalDay:
                g.add((self.uriRef, PUBC["additionalDay"], additionalDay))

        if self.increaseAmount:
            for increaseAmount in self.increaseAmount:
                g.add((self.uriRef, PUBC["increaseAmount"], increaseAmount))

        if self.reductionAmount:
            for reductionAmount in self.reductionAmount:
                g.add((self.uriRef, PUBC["reductionAmount"], reductionAmount))

        if self.variantDate:
            for variantDate in self.variantDate:
                g.add((self.uriRef, PUBC["variantDate"], variantDate))

        if self.variantType:
            for variantType in self.variantType:
                g.add((self.uriRef, PUBC["variantType"], variantType))
