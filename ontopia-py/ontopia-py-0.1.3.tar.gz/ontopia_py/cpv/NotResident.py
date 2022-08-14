from ..ns import *
from .Person import Person


class NotResident(Person):
    __type__ = CPV["NotResident"]
