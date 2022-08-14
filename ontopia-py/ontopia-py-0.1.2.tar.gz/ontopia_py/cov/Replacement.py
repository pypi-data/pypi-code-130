from ..ns import *
from .ChangeEvent import ChangeEvent


class Replacement(ChangeEvent):
    __type__ = COV["Replacement"]
