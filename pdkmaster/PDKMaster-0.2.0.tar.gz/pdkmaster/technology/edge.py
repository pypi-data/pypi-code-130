# SPDX-License-Identifier: GPL-2.0-or-later OR AGPL-3.0-or-later OR CERN-OHL-S-2.0+
import abc
from typing import Union

from ..typing import SingleOrMulti
from .. import _util
from . import property_ as prp, mask as msk


__all__ = ["MaskEdge"]


_MaskOrEdge = Union[msk._Mask, "_Edge"]


class _EdgeProperty(prp.Property):
    def __init__(self, *, edge: "_Edge", name: str):
        super().__init__(str(edge) + "." + name)
        self.edge = edge
        self.prop_name = name


class _DualEdgeProperty(prp.Property):
    def __init__(self, *,
        edge1: "_Edge", edge2: _MaskOrEdge, name: str, commutative: bool, allow_mask2: bool,
    ):
        assert (
            isinstance(edge2, _Edge) or (isinstance(edge2, msk._Mask) and allow_mask2)
        ), "Internal error"

        if commutative:
            full_name = f"{name}({edge1.name},{edge2.name})"
        else:
            full_name = f"{edge1.name}.{name}({edge2.name})"
        super().__init__(full_name)

        self.edge1 = edge1
        self.edge2 = edge2
        self.prop_name = name


class _Edge(abc.ABC):
    @abc.abstractmethod
    def __init__(self, *, name: str):
        self.name = name

        self.length = _EdgeProperty(edge=self, name="length")

    def __str__(self):
        return self.name

    def enclosed_by(self, other: _MaskOrEdge):
        return _DualEdgeProperty(
            edge1=self, edge2=other, name="enclosed_by",
            commutative=False, allow_mask2=True,
        )

    def interact_with(self, other: _MaskOrEdge):
        return _DualEdgeOperation(
            edge1=self, edge2=other, name="interact_with", allow_mask2=True,
        )


class _DualEdgeOperation(_Edge):
    def __init__(self, *,
        edge1: _Edge, edge2: _MaskOrEdge, name: str, allow_mask2: bool=False,
    ):
        assert (
            isinstance(edge2, _Edge) or (allow_mask2 and isinstance(edge2, msk._Mask))
        ), "Internal error"

        super().__init__(name=f"{edge1.name}.{name}({edge2.name})")
        self.edge1 = edge1
        self.edge2 = edge2
        self.operation = name


class MaskEdge(_Edge):
    def __init__(self, mask: msk._Mask):
        self.mask = mask

        super().__init__(name=f"edge({mask.name})")


class Join(_Edge):
    def __init__(self, edges: SingleOrMulti[_Edge].T):
        self.edges = edges = _util.v2t(edges)

        super().__init__(name="join({})".format(",".join(str(edge) for edge in edges)))


class Intersect(_Edge):
    def __init__(self, edges: SingleOrMulti[_MaskOrEdge].T):
        edges = _util.v2t(edges)
        if not any(isinstance(edge, _Edge) for edge in edges):
            raise ValueError("at least one element of edges has to be of type 'Edge'")
        self.edges = edges

        super().__init__(name="intersect({})".format(",".join(str(edge) for edge in edges)))
