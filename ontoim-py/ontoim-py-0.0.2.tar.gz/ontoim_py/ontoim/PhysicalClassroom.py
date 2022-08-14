from __future__ import annotations

from typing import TYPE_CHECKING

from ..ns import *
from .Classroom import Classroom

if TYPE_CHECKING:
    from ontopia_py.clv.Address import Address
    from rdflib import Graph


class PhysicalClassroom(Classroom):
    __type__ = ONTOIM["PhysicalClassroom"]

    hasAddress: Address = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.hasAddress:
            g.add((self.uriRef, ONTOIM["hasAddress"], self.hasAddress.uriRef))
