from __future__ import annotations

from ..ns import *
from .ProcedureChangeEvent import ProcedureChangeEvent


class Variant(ProcedureChangeEvent):
    __type__ = PUBC["Variant"]
