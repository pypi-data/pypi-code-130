from ..ns import *
from .AlivePerson import AlivePerson


class ForeignCitizen(AlivePerson):
    __type__ = CPV["ForeignCitizen"]
