"""
Implements the `Matrix` class (see `help(Matrix)`).
"""

from __future__ import annotations

from fractions import Fraction
from itertools import chain, islice
from operator import (
    mul as mul_operator,
    truediv as truediv_operator,
    add as add_operator,
    sub as sub_operator,
)
from types import EllipsisType
from typing import Any, Callable, Iterable, Final

from .header import DimensionMismatchError

__all__ = ("Matrix",)


class Matrix:
    """
    Expresses the mathematical notion of a rational-valued matrix in
        native Python datastructures and datatypes while providing an
        assortment of tools to perform basic matrix manipulations.

    `Matrix` objects are considered non-mutable, which means that for
        the life of an object it cannot be meaningfully modified[^1].
        Matrices are, therefore, hashable (using
        `hash(matrix_instance)`).

    [^1]: If you need to modify a `Matrix`, look into the
        `matrix_instance.elements` property.
    """

    __slots__ = ("_data", "_shape", "_hash", "_iter_index")

    def __init__(
        self,
        initializer: Iterable[Iterable[float | Fraction]],
    ) -> None:
        """
        Initializes a new instance of the `Matrix` class.

        Arguments
        - initializer: A 2D iterable that will be used to construct the
            matrix.

        Possible Errors
        - ValueError: If the initializer has no elements, or if the
            initializer is jagged (not rectangular).
        """
        # Capture the data - necessary because the initializer could be
        # mutable, or a generator.
        data = tuple(
            tuple(Fraction(item) for item in row) for row in initializer
        )
        # Check the data shape
        if len(data) <= 0 or len(data[0]) <= 0:
            raise ValueError("matrices must have at least one element")
        num_of_cols = len(data[0])
        for row in data:
            if len(row) != num_of_cols:
                raise ValueError("matrices must be rectangular (not jagged)")
        # Set instance variables
        self._data: Final[tuple[tuple[Fraction, ...], ...]] = data
        self._shape: Final[tuple[int, int]] = (len(data), num_of_cols)
        self._hash: int | None = None
        self._iter_index: int | None = None

    def __len__(
        self,
    ) -> int:
        """
        Returns the total number of elements in this matrix.
        """
        return self._shape[0] * self._shape[1]

    def __getitem__(
        self,
        key: tuple[int, int],
    ) -> Fraction:
        """
        Returns the item at a specified coordinate in this matrix.

        Arguments
        - key: The 0-indexed row-column coordinates of the desired
            element.

        Possible Errors
        - IndexError: If the row or column index is out of bounds.
        """
        try:
            return self._data[key[0]][key[1]]
        except IndexError:
            raise IndexError(
                f"index out of bounds, expected index in "
                f"([0, {self._shape[0]}), [0, {self._shape[0]})) but "
                f"received ({key[0]}, {key[1]})"
            )

    def __iter__(
        self,
    ) -> Matrix:
        """
        Initializes this matrix for iteration using the `__next__`
            method.
        """
        self._iter_index = 0
        return self

    def __next__(
        self,
    ) -> tuple[Fraction, ...]:
        """
        Returns the next row of this matrix if the `__iter__` method has
            been used to initialize iteration.

        Possible Errors
        - RuntimeError: If iteration was not properly initialized.

        Notes
        - Raises `StopIteration` when all rows have been iterated over.
        """
        if self._iter_index is None:
            raise RuntimeError("iterator not initialized (use 'iter')")
        if self._iter_index >= self._shape[0]:
            self._iter_index = None
            raise StopIteration
        result = self._data[self._iter_index]
        self._iter_index += 1
        return result

    def __str__(
        self,
    ) -> str:
        """
        Returns a "pretty" string representation of this matrix.
        """
        return self._string_format(
            10,
            10,
            lambda f: (
                "%.3g" % (f.numerator if f.denominator == 1 else float(f))
            ),
        )

    def __repr__(
        self,
    ) -> str:
        """
        Returns a reproduction string representation of this matrix.

        Notes
        - Assuming all relevant libraries have been imported, the
            reproduction string can be run as valid Python to create
            an exact copy of this matrix.
        """
        obj_name = self.__class__.__name__
        initializer = "[\n        [{}],\n    ]".format(
            "],\n        [".join(
                ", ".join(repr(item) for item in row) for row in self._data
            )
        )
        return f"{obj_name}(\n    initializer={initializer},\n)"

    def __matmul__(
        self,
        other: Matrix,
    ) -> Matrix:
        """
        Returns the matrix product of this and another
            matrix.

        Arguments
        - other: The right-hand-side operand to matrix multiplication.

        Possible Errors
        - DimensionMismatchError: If the column count of `self` does not
            match the row count of `other`.
        """
        inner_dim = self._shape[1]
        if inner_dim != other._shape[0]:
            raise DimensionMismatchError(
                f"left side columns ({self._shape[1]}) "
                f"do not equal right side rows ({other._shape[0]}), "
                "did you mean to find the Hadamard (element-wise) product "
                "instead? ('*' operator)"
            )
        return Matrix(
            (
                sum((self[row, i] * other[i, col] for i in range(inner_dim)))
                for col in range(other._shape[1])
            )
            for row in range(self._shape[0])
        )

    def __mul__(
        self,
        other: Matrix | float | Fraction,
    ) -> Matrix:
        """
        Calculates the element-wise product of this matrix and either
            another matrix or a single number.

        Arguments
        - other: The left-hand-side operand.

        Possible Errors
        - DimensionMismatchError: If `other` is a Matrix and does not
            have the required shape.

        Notes
        - To calculate the matrix product of two matrices, use the
            `__matmul__` (at-sign) operator.
        """
        return self._elwise_operate(other, True, mul_operator)

    def __rmul__(
        self,
        other: float | Fraction,
    ) -> Matrix:
        """
        Calculates the element-wise product of this matrix and either
            another matrix or a single number (if this matrix is the
            right-hand-side operand).

        Arguments
        - other: The right-hand-side operand.

        Possible Errors
        - DimensionMismatchError: If `other` is a Matrix and does not
            have the required shape.

        Notes
        - To calculate the matrix product of two matrices, use the
            `__matmul__` (at-sign) operator.
        """
        return self._elwise_operate(other, False, mul_operator)

    def __truediv__(
        self,
        other: Matrix | float | Fraction,
    ) -> Matrix:
        """
        Calculates the element-wise quotient of this matrix and either
            another matrix or a single number.

        Arguments
        - other: The left-hand-side operand.

        Possible Errors
        - DimensionMismatchError: If `other` is a Matrix and does not
            have the required shape.
        - ZeroDivisionError: If `other` is zero, or is a matrix that
            contains a zero anywhere.
        """
        return self._elwise_operate(other, True, truediv_operator)

    def __rtruediv__(
        self,
        other: float | Fraction,
    ) -> Matrix:
        """
        Calculates the element-wise quotient of this matrix and either
            another matrix or a single number (if this matrix is the
            right-hand-side operand).

        Arguments
        - other: The right-hand-side operand.

        Possible Errors
        - DimensionMismatchError: If `other` is a Matrix and does not
            have the required shape.
        - ZeroDivisionError: If `other` is zero, or is a matrix that
            contains a zero anywhere.
        """
        return self._elwise_operate(other, False, truediv_operator)

    def __add__(
        self,
        other: Matrix | float | Fraction,
    ) -> Matrix:
        """
        Calculates the element-wise sum of this matrix and either
            another matrix or a single number.

        Arguments
        - other: The left-hand-side operand.

        Possible Errors
        - DimensionMismatchError: If `other` is a Matrix and does not
            have the required shape.
        """
        return self._elwise_operate(other, True, add_operator)

    def __radd__(
        self,
        other: float | Fraction,
    ) -> Matrix:
        """
        Calculates the element-wise sum of this matrix and either
            another matrix or a single number (if this matrix is the
            right-hand-side operand).

        Arguments
        - other: The right-hand-side operand.

        Possible Errors
        - DimensionMismatchError: If `other` is a Matrix and does not
            have the required shape.
        """
        return self._elwise_operate(other, False, add_operator)

    def __sub__(
        self,
        other: Matrix | float | Fraction,
    ) -> Matrix:
        """
        Calculates the element-wise difference of this matrix and either
            another matrix or a single number.

        Arguments
        - other: The left-hand-side operand.

        Possible Errors
        - DimensionMismatchError: If `other` is a Matrix and does not
            have the required shape.
        """
        return self._elwise_operate(other, True, sub_operator)

    def __rsub__(
        self,
        other: float | Fraction,
    ) -> Matrix:
        """
        Calculates the element-wise difference of this matrix and either
            another matrix or a single number (if this matrix is the
            right-hand-side operand).

        Arguments
        - other: The right-hand-side operand.

        Possible Errors
        - DimensionMismatchError: If `other` is a Matrix and does not
            have the required shape.
        """
        return self._elwise_operate(other, False, sub_operator)

    def __neg__(
        self,
    ) -> Matrix:
        """
        Calculates the element-wise negation of this matrix.
        """
        return self._elwise_operate(-1, True, mul_operator)

    def __eq__(
        self,
        other: Any,
    ) -> bool:
        """
        Compares this matrix to an object, returns `True` if and only
            if the right-hand side is a matrix with the same dimensions
            as this matrix, such that every element in this matrix is
            equal to every corresponding element in the `other` matrix
            (otherwise returns `False`).

        Arguments
        - other: The object this vector is to be compared to.
        """
        if not isinstance(other, Matrix):
            return False
        if self._hash is not None and other._hash is not None:
            if hash(self) != hash(other):
                return False
        if self._shape != other._shape:
            return False
        for row in range(self._shape[0]):
            for col in range(self._shape[1]):
                if self[row, col] != other[row, col]:
                    return False
        return True

    def __or__(
        self,
        other: Matrix,
    ) -> Matrix:
        """
        Concatenates the rows of this matrix with the rows of the
            `other` matrix.

        Arguments
        - other: The right-hand side rows to append.

        Possible Errors
        - DimensionMismatchError: If the two matrices have unequal row
            counts.
        """
        return self.cat(other, horizontally=True)

    def __hash__(
        self,
    ) -> int:
        """
        Returns the hash of this matrix.
        """
        if self._hash is None:
            self._hash = hash(self._data)
        return self._hash

    def cat(
        self,
        other: Matrix,
        horizontally: bool = True,
    ) -> Matrix:
        """
        Concatenates the rows of this matrix with the rows of the
            `other` matrix.

        Arguments
        - other: The right-hand side rows to append.
        - horizontally: Whether to concatenate the matrices horizontally
            (when true) or vertically (when false).
            Optional, defaults to true.

        Possible Errors
        - DimensionMismatchError: If the two matrices have unequal shape
            dimensions perpendicular to the direction of concatenation.
        """
        if horizontally:
            if self._shape[0] != other._shape[0]:
                raise DimensionMismatchError(
                    f"left side rows ({self._shape[0]}) "
                    f"do not equal right side rows ({other._shape[0]}), "
                    "cannot augment columns"
                )
            return Matrix(
                (
                    chain(self_row, other_row)
                    for self_row, other_row in zip(self._data, other._data)
                )
            )
        else:
            if self._shape[1] != other._shape[1]:
                raise DimensionMismatchError(
                    f"top side columns ({self._shape[0]}) "
                    f"do not equal bottom side columns ({other._shape[0]}), "
                    "cannot append rows"
                )
            return Matrix(chain(self._data, other._data))

    def get_slice(
        self,
        rows: tuple[int | EllipsisType, int | EllipsisType]
        | EllipsisType
        | int = ...,
        cols: tuple[int | EllipsisType, int | EllipsisType]
        | EllipsisType
        | int = ...,
    ) -> Matrix:
        """
        Crops unselected rows and columns from this matrix and
            returns the result.

        Arguments
        - rows: The rows to keep. If a tuple, this specifies the
            starting coordinate (inclusive) followed by the ending
            coordinate (exclusive). If an integer, this specifies a
            single row. If ellipses, this specifies all rows.
            Optional, defaults to ellipses. Ellipses signify either
            "from the beginning" or "to the end" inside tuples, for
            positions 0 and 1, respectively.
        - cols: The columns to keep. If a tuple, this specifies the
            starting coordinate (inclusive) followed by the ending
            coordinate (exclusive). If an integer, this specifies a
            single column. If ellipses, this specifies all columns.
            Optional, defaults to ellipses. Ellipses signify either
            "from the beginning" or "to the end" inside tuples, for
            positions 0 and 1, respectively.

        Possible Errors
        - IndexError: If the slice would create a matrix with zero
            elements.
        """
        if isinstance(rows, EllipsisType):
            rows = (0, self._shape[0])
        elif isinstance(rows, int):
            rows = (rows, rows + 1)
        if isinstance(cols, EllipsisType):
            cols = (0, self._shape[1])
        elif isinstance(cols, int):
            cols = (cols, cols + 1)
        rows = (
            0 if isinstance(rows[0], EllipsisType) else max(rows[0], 0),
            (
                self._shape[0]
                if isinstance(rows[1], EllipsisType)
                else min(rows[1], self._shape[0])
            ),
        )
        cols = (
            0 if isinstance(cols[0], EllipsisType) else max(cols[0], 0),
            (
                self._shape[1]
                if isinstance(cols[1], EllipsisType)
                else min(cols[1], self._shape[1])
            ),
        )
        if rows[0] >= rows[1] or cols[0] >= cols[1]:
            raise IndexError("matrices must have at least one element")

        return Matrix(
            (islice(row, *cols) for row in islice(self._data, *rows))
        )

    def limit_denominator(
        self,
        max_denominator: int,
    ) -> Matrix:
        """
        Limits the denominator of all `Fraction` objects in this
            matrix to some upper bound.

        Arguments
        - max_denominator: The largest allowed denominator.

        Possible Errors
        - ZeroDivisionError: If `max_denominator` is 0.
        """
        if max_denominator == 0:
            raise ZeroDivisionError("max denominator may not be 0")
        return Matrix(
            (
                (
                    (item.limit_denominator(max_denominator) for item in row)
                    for row in self._data
                )
            )
        )

    # PROPERTIES

    @property
    def diagonal(
        self,
    ) -> Iterable[Fraction]:
        for i in range(min(self._shape)):
            yield self[i, i]

    @property
    def elements(
        self,
    ) -> list[list[Fraction]]:
        return [[item for item in row] for row in self._data]

    @property
    def shape(
        self,
    ) -> tuple[int, int]:
        return self._shape

    # PRIVATE/PROTECTED METHODS

    def _elwise_operate(
        self,
        other: Matrix | float | Fraction,
        self_side_left: bool,
        operation: Callable[
            [float | Fraction, float | Fraction],
            float | Fraction,
        ],
    ) -> Matrix:
        """
        Returns a matrix that results from the element-wise operation of
            two matrices (or one matrix and a number).

        Arguments
        - other: The right-hand side operand, can be either a matrix or
            a number (numbers are interpreted as homogenous matrices of
            the same shape as `self`).
        - self_side_left: Whether `self` is the left operand (true), or
            the right operand (false).
        - operation: The arbitrary operation applied to two elements to
            create a single result.

        Possible Errors
        - DimensionMismatchError: If `other` is a Matrix and does not
            have the required shape.

        Notes
        - The operation specified in `operation` may raise errors. These
            will not be caught by this method.
        - This is a private method not meant to be exposed.
        """
        if isinstance(other, Matrix):
            if self._shape != other._shape:
                order = (
                    ("left", "right") if self_side_left else ("right", "left")
                )
                raise DimensionMismatchError(
                    f"{order[0]} side shape {self._shape} "
                    f"does not equal {order[1]} side shape {other._shape}"
                )
            if self_side_left:
                return Matrix(
                    (
                        operation(self_item, other_item)
                        for self_item, other_item in zip(*rows)
                    )
                    for rows in zip(self._data, other._data)
                )
            else:
                return Matrix(
                    (
                        operation(other_item, self_item)
                        for self_item, other_item in zip(*rows)
                    )
                    for rows in zip(self._data, other._data)
                )

        else:
            if self_side_left:
                return Matrix(
                    (operation(item, other) for item in row)
                    for row in self._data
                )
            else:
                return Matrix(
                    (operation(other, item) for item in row)
                    for row in self._data
                )

    def _string_format(
        self,
        max_rows: int,
        max_cols: int,
        element_formatter: Callable[[Fraction], str],
    ) -> str:
        """
        Returns a "pretty" string representation of this matrix.

        Arguments
        - max_rows: The maximum number of rows to print.
        - max_cols: The maximum number of columns to print.
        - element_formatter: The operation applied to each element to
            convert it to a string.

        Notes
        - TODO: Refactor to make this more readable.
        - This is a private method not meant to be exposed.
        """

        def format_to_str(n: Fraction, row: int, col: int) -> str:
            if row >= max_rows:
                if col >= max_cols:
                    return "\u22F1"
                return "\u22EE"
            elif col >= max_cols:
                return "\u22EF"
            else:
                return element_formatter(n)

        element_strs = [
            [
                format_to_str(self[row, col], row, col)
                for col in range(min(self._shape[1], max_cols + 1))
            ]
            for row in range(min(self._shape[0], max_rows + 1))
        ]
        column_lengths = [
            max(
                (
                    len(element_strs[row][col])
                    for row in range(min(len(element_strs), max_rows + 1))
                )
            )
            for col in range(min(len(element_strs[0]), max_cols + 1))
        ]
        for row in range(len(element_strs)):
            for col in range(len(element_strs[row])):
                element_strs[row][col] = element_strs[row][col].center(
                    column_lengths[col]
                )

        dat_str = f" \u2502\n\u2502 ".join(
            ("  ".join(row) for row in element_strs)
        )
        space = " " * (sum(column_lengths) + (2 * len(column_lengths)))
        return (
            f"\u250C{space}\u2510\n"
            f"\u2502 {dat_str} \u2502"
            f" (size: {self._shape[0]}\u00D7{self._shape[1]})\n"
            f"\u2514{space}\u2518"
        )
