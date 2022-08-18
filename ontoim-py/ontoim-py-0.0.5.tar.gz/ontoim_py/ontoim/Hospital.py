from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..ns import *
from .Facility import Facility

if TYPE_CHECKING:
    from rdflib import Graph, Literal

    from .HospitalDepartment import HospitalDepartment


class Hospital(Facility):
    __type__ = ONTOIM["Hospital"]

    hasHospitalDepartment: List[HospitalDepartment] = None
    totalNumberOfBeds: Literal = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.hasHospitalDepartment:
            for hasHospitalDepartment in self.hasHospitalDepartment:
                g.add(
                    (self.uriRef, ONTOIM["hasHospitalDepartment"], hasHospitalDepartment.uriRef))

        if self.totalNumberOfBeds:
            g.add(
                (self.uriRef, ONTOIM["totalNumberOfBeds"], self.totalNumberOfBeds))
