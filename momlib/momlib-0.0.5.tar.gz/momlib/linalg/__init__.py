"""
Provides linear algebraic objects and and tools.
"""


from .header import (
    LinearDependenceError,
    RectangularMatrixError,
    DimensionMismatchError,
)
from .matrix import Matrix
from .vector import Vector
from .tools import (
    cross,
    determinant,
    distance,
    get_vectors,
    homogenous_matrix,
    homogenous_vector,
    identity,
    inverse,
    laplace_expansion,
    magnitude,
    matcat,
    matrix_power,
    normalize,
    orthogonalize,
    rank,
    row_reduce,
    transpose,
)

__all__ = (
    "LinearDependenceError",
    "RectangularMatrixError",
    "DimensionMismatchError",
    "Matrix",
    "Vector",
    "cross",
    "determinant",
    "distance",
    "get_vectors",
    "homogenous_matrix",
    "homogenous_vector",
    "identity",
    "inverse",
    "laplace_expansion",
    "magnitude",
    "matcat",
    "matrix_power",
    "normalize",
    "orthogonalize",
    "cross",
    "rank",
    "row_reduce",
    "transpose",
)
