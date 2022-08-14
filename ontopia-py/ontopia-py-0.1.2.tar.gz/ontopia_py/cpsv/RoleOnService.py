from __future__ import annotations

from rdflib import URIRef

from ..ns import *
from ..ro.Role import Role


class RoleOnService(Role):
    __type__ = CPSV["RoleOnService"]


class Concessionaire(RoleOnService):
    def __init__(self):
        self.uriRef = URIRef(CPSV["Concessionaire"])


class Creator(RoleOnService):
    def __init__(self):
        self.uriRef = URIRef(CPSV["Creator"])


class Maintainer(RoleOnService):
    def __init__(self):
        self.uriRef = URIRef(CPSV["Maintainer"])


class Provider(RoleOnService):
    def __init__(self):
        self.uriRef = URIRef(CPSV["Provider"])


class RightsHolder(RoleOnService):
    def __init__(self):
        self.uriRef = URIRef(CPSV["RightsHolder"])


class User(RoleOnService):
    def __init__(self):
        self.uriRef = URIRef(CPSV["User"])
