# SPDX-License-Identifier: GPL-2.0-or-later OR AGPL-3.0-or-later OR CERN-OHL-S-2.0+
from typing import Generic, Iterable, Tuple, Dict, Optional, Union, TypeVar

_elem_type = TypeVar("_elem_type")

class SingleOrMulti(Generic[_elem_type]):
    """Type to represent a single value or an iterable of a value of
    a given type.

    Example:
        `SingleOrMulti[int].T` == `Union[int, Interable[int]]`
    """
    T = Union[_elem_type, Iterable[_elem_type]]

class OptSingleOrMulti(Generic[_elem_type]):
    """`OptSingleOrMulti[T].T` == `Optional[SingleOrMulti[T].T]`"""
    T = Optional[Union[_elem_type, Iterable[_elem_type]]]

IntFloat = Union[int, float]
GDSLayerSpec = Union[int, Tuple[int, int]]
# We define the gds_layer lookup table by str,
# Doing it directly by DesignMask would be preferred but this leads
# to complicated recursive imports
GDSLayerSpecDict = Dict[str, GDSLayerSpec]
