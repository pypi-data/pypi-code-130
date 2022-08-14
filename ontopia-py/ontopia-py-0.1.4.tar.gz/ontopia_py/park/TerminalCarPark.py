from __future__ import annotations

from ..ns import *
from .CarPark import CarPark


class TerminalCarPark(CarPark):
    __type__ = PARK["TerminalCarPark"]
