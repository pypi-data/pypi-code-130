from __future__ import annotations

from rdflib import URIRef

from ..l0.Characteristic import Characteristic
from ..ns import *


class TransparencyActivityTypology(Characteristic):
    __type__ = TRANSP["TransparencyActivityTypology"]


class TransparencyArchiveActivity(TransparencyActivityTypology):
    def __init__(self):
        self.uriRef = URIRef(TRANSP["TransparencyArchiveActivity"])


class TransparencyPublicationActivity(TransparencyActivityTypology):
    def __init__(self):
        self.uriRef = URIRef(TRANSP["TransparencyPublicationActivity"])


class TransparencyUpdateActivity(TransparencyActivityTypology):
    def __init__(self):
        self.uriRef = URIRef(TRANSP["TransparencyUpdateActivity"])
