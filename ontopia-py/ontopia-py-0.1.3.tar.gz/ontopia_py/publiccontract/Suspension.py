from __future__ import annotations

from ..ns import *
from .ProcedureChangeEvent import ProcedureChangeEvent


class Suspension(ProcedureChangeEvent):
    __type__ = PUBC["Suspension"]
