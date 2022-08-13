from ..ns import *
from .ChangeEvent import ChangeEvent


class Closing(ChangeEvent):
    __type__ = COV["Closing"]
