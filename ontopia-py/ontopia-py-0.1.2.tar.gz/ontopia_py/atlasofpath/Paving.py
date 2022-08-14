from __future__ import annotations

from rdflib import URIRef

from ..l0.Characteristic import Characteristic
from ..ns import *


class Paving(Characteristic):
    __type__ = PATHS["Paving"]


class Asphalt(Paving):
    def __init__(self):
        self.uriRef = URIRef(PATHS["asphalt"])