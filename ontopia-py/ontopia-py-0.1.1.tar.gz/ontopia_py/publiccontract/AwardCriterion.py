from __future__ import annotations

from rdflib import URIRef

from ..l0.Characteristic import Characteristic
from ..ns import *


class AwardCriterion(Characteristic):
    __type__ = PUBC["AwardCriterion"]


class LowestPrice(AwardCriterion):
    def __init__(self):
        self.uriRef = URIRef(PUBC["LowestPrice"])


class MostEconomicallyAdvantageousTender(AwardCriterion):
    def __init__(self):
        self.uriRef = URIRef(PUBC["MostEconomicallyAdvantageousTender"])
