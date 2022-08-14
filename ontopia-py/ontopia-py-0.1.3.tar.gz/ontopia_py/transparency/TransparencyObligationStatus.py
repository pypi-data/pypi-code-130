from __future__ import annotations

from rdflib import URIRef

from ..l0.Characteristic import Characteristic
from ..ns import *


class TransparencyObligationStatus(Characteristic):
    __type__ = TRANSP["TransparencyObligationStatus"]


class Deprecated(TransparencyObligationStatus):
    def __init__(self):
        self.uriRef = URIRef(TRANSP["Deprecated"])


class InForce(TransparencyObligationStatus):
    def __init__(self):
        self.uriRef = URIRef(TRANSP["InForce"])