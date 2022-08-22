"""
Implements the `Vector` class (see `help(Vector)`).
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

__all__ = ("Vector",)


class Vector:
    """
    Expresses the mathematical notion of a rational-valued Vector in
        native Python datastructures and datatypes while providing an
        assortment of tools to perform basic vector manipulations.

    `Vector` objects are considered non-mutable, which means that for
        the life of an object it cannot be meaningfully modified[^1].
        Vectors are, therefore, hashable (using
        `hash(vector_instance)`).

    [^1]: If you need to modify a `Vector`, look into the
        `vector_instance.elements` property.
    """

    __slots__ = ("_data", "_length", "_hash", "_iter_index")

    def __init__(
        self,
        initializer: Iterable[float | Fraction],
    ) -> None:
        """
        Initializes a new instance of the `Vector` class.

        Arguments
        - initializer: An iterable that will be used to construct the
            vector.

        Possible Errors
        - ValueError: If the initializer has no elements.
        """
        data = tuple(Fraction(item) for item in initializer)
        if len(data) <= 0:
            raise ValueError("vectors must have at least one element")
        self._data: Final[tuple[Fraction, ...]] = data
        self._length: Final[int] = len(data)
        self._hash: int | None = None
        self._iter_index: int | None = None

    def __len__(
        self,
    ) -> int:
        """
        Returns the total number of elements in this vector.
        """
        return self._length

    def __getitem__(
        self,
        key: int,
    ) -> Fraction:
        """
        Returns a copy of the item at a given position.

        Arguments
        - key: The 0-indexed position of the desired element.

        Possible Errors
        - IndexError: If the key index is out of bounds.
        """
        try:
            return self._data[key]
        except IndexError:
            raise IndexError(
                f"index out of bounds, expected index in "
                f"[0, {self._length}) but received {key}"
            )

    def __iter__(
        self,
    ) -> Vector:
        """
        Initializes this vector for iteration using the `__next__`
        method.
        """
        self._iter_index = 0
        return self

    def __next__(
        self,
    ) -> Fraction:
        """
        Returns the next item in a row-wise traversal of this vector
            if the `__iter__` method has been used to initialize
            iteration.

        Possible Errors
        - RuntimeError: If iteration was not properly initialized.

        Notes
        - Raises `StopIteration` when all items have been iterated over.
        """
        if self._iter_index is None:
            raise RuntimeError("iterator not initialized")
        if self._iter_index >= self._length:
            self._iter_index = None
            raise StopIteration
        result = self._data[self._iter_index]
        self._iter_index += 1
        return result

    def __str__(
        self,
    ) -> str:
        """
        Returns a "pretty" string representation of this vector.
        """
        return self._string_format(
            10,
            lambda f: (
                "%.3g" % (f.numerator if f.denominator == 1 else float(f))
            ),
        )

    def __repr__(
        self,
    ) -> str:
        """
        Returns a reproduction string representation of this vector.
        """
        obj_name = self.__class__.__name__
        initializer = "[{}]".format(
            ", ".join(repr(item) for item in self._data)
        )
        return f"{obj_name}(\n    initializer={initializer},\n)"

    def __matmul__(
        self,
        other: Vector,
    ) -> Fraction:
        """
        Calculates the dot product of this and another vector.

        Arguments
        - other: The right-hand-side operand to dot multiplication.

        Possible Errors
        - DimensionMismatchError: If the two vectors have different
            lengths.

        Notes
        - To calculate the element-wise product of two vectors, use the
            `__mul__` (asterisk) operator.
        """
        if self._length != other._length:
            raise DimensionMismatchError(
                f"left side length ({self._length}) "
                f"does not match right side length ({other._length})"
            )
        return sum(
            (
                self_item * other_item
                for self_item, other_item in zip(self._data, other._data)
            ),
            start=Fraction(0),
        )

    def __mul__(
        self,
        other: Vector | float | Fraction,
    ) -> Vector:
        """
        Calculates the element-wise product of this vector and either
            another vector or a single number.

        Arguments
        - other: The left-hand-side operand.

        Possible Errors
        - DimensionMismatchError: If `other` is a Vector and does not
            have the required shape.

        Notes
        - To calculate the dot product of two matrices, use the
            `__matmul__` (at-sign) operator.
        """
        return self._elwise_operate(other, True, mul_operator)

    def __rmul__(
        self,
        other: float | Fraction,
    ) -> Vector:
        """
        Calculates the element-wise product of this vector and either
            another vector or a single number (if this vector is the
            right-hand-side operand).

        Arguments
        - other: The right-hand-side operand.

        Possible Errors
        - DimensionMismatchError: If `other` is a Vector and does not
            have the required shape.

        Notes
        - To calculate the dot product of two matrices, use the
            `__matmul__` (at-sign) operator.
        """
        return self._elwise_operate(other, False, mul_operator)

    def __truediv__(
        self,
        other: Vector | float | Fraction,
    ) -> Vector:
        """
        Calculates the element-wise quotient of this vector and either
            another vector or a single number.

        Arguments
        - other: The left-hand-side operand.

        Possible Errors
        - DimensionMismatchError: If `other` is a Vector and does not
            have the required shape.
        - ZeroDivisionError: If `other` is zero, or is a vector that
            contains a zero anywhere.
        """
        return self._elwise_operate(other, True, truediv_operator)

    def __rtruediv__(
        self,
        other: float | Fraction,
    ) -> Vector:
        """
        Calculates the element-wise quotient of this vector and either
            another vector or a single number (if this vector is the
            right-hand-side operand).

        Arguments
        - other: The right-hand-side operand.

        Possible Errors
        - DimensionMismatchError: If `other` is a Vector and does not
            have the required shape.
        - ZeroDivisionError: If `other` is zero, or is a vector that
            contains a zero anywhere.
        """
        return self._elwise_operate(other, False, truediv_operator)

    def __add__(
        self,
        other: Vector | float | Fraction,
    ) -> Vector:
        """
        Calculates the element-wise sum of this vector and either
            another vector or a single number.

        Arguments
        - other: The left-hand-side operand.

        Possible Errors
        - DimensionMismatchError: If `other` is a Vector and does not
            have the required shape.
        """
        return self._elwise_operate(other, True, add_operator)

    def __radd__(
        self,
        other: float | Fraction,
    ) -> Vector:
        """
        Calculates the element-wise sum of this vector and either
            another vector or a single number (if this vector is the
            right-hand-side operand).

        Arguments
        - other: The right-hand-side operand.

        Possible Errors
        - DimensionMismatchError: If `other` is a Vector and does not
            have the required shape.
        """
        return self._elwise_operate(other, False, add_operator)

    def __sub__(
        self,
        other: Vector | float | Fraction,
    ) -> Vector:
        """
        Calculates the element-wise difference of this vector and either
            another vector or a single number.

        Arguments
        - other: The left-hand-side operand.

        Possible Errors
        - DimensionMismatchError: If `other` is a Vector and does not
            have the required shape.
        """
        return self._elwise_operate(other, True, sub_operator)

    def __rsub__(
        self,
        other: float | Fraction,
    ) -> Vector:
        """
        Calculates the element-wise difference of this vector and either
            another vector or a single number (if this vector is the
            right-hand-side operand).

        Arguments
        - other: The right-hand-side operand.

        Possible Errors
        - DimensionMismatchError: If `other` is a Vector and does not
            have the required shape.
        """
        return self._elwise_operate(other, False, sub_operator)

    def __neg__(
        self,
    ) -> Vector:
        """
        Calculates the element-wise negation of this vector.
        """
        return self._elwise_operate(-1, True, mul_operator)

    def __eq__(
        self,
        other: Any,
    ) -> bool:
        """
        Compares this vector to an object, returns true if and only
            if the right-hand side is a vector with the same length
            as this vector, such that every element in this vector is
            equal to every corresponding element in the `other` vector
            (otherwise returns false).

        Arguments
        - other: The object this vector is to be compared to.
        """
        if not isinstance(other, Vector):
            return False
        if self._hash is not None and other._hash is not None:
            if hash(self) != hash(other):
                return False
        length = self._length
        if length != other._length:
            return False
        for i in range(length):
            if self[i] != other[i]:
                return False
        return True

    def __hash__(
        self,
    ) -> int:
        """
        Returns the hash of this vector.
        """
        if self._hash is None:
            self._hash = hash(self._data)
        return self._hash

    def cat(
        self,
        other: Vector | float | Fraction,
    ) -> Vector:
        """
        Concatenates the elements of this vector with the elements of
            the `other` vector.

        Arguments
        - other: The vector to append to this vector.

        Possible Errors
        - DimensionMismatchError: If the two vectors have unequal
            lengths.
        """
        if isinstance(other, Vector):
            return Vector(chain(self, other))
        else:
            return Vector(chain(self, [other]))

    def get_slice(
        self,
        items: tuple[int | EllipsisType, int | EllipsisType],
    ) -> Vector:
        """
        Crops unselected elements from this vector and returns the
            result.

        Arguments
        - items: The range of elements to keep. This specifies the
            starting coordinate (inclusive) followed by the ending
            coordinate (exclusive). Ellipses signify either "from the
            beginning" or "to the end" inside tuples, for positions 0
            and 1, respectively.

        Possible Errors
        - IndexError: If the slice would create a vector with zero
            elements.
        """
        items = (
            0 if isinstance(items[0], EllipsisType) else max(items[0], 0),
            (
                self._length
                if isinstance(items[1], EllipsisType)
                else min(items[1], self._length)
            ),
        )
        if items[0] >= items[1]:
            raise IndexError("vectors must have at least one element")
        return Vector(islice(self._data, *items))

    def limit_denominator(
        self,
        max_denominator: int,
    ) -> Vector:
        """
        Limits the denominator of all `Fraction` objects in this
            vector to some upper bound.

        Arguments
        - max_denominator: The largest allowed denominator.

        Possible Errors
        - ZeroDivisionError: If `max_denominator` is 0.
        """
        if max_denominator == 0:
            raise ZeroDivisionError("max denominator may not be 0")
        return Vector(
            item.limit_denominator(max_denominator) for item in self._data
        )

    # PROPERTIES

    @property
    def elements(
        self,
    ) -> list[Fraction]:
        return [item for item in self._data]

    # PRIVATE/PROTECTED METHODS

    def _elwise_operate(
        self,
        other: Vector | float | Fraction,
        self_side_left: bool,
        operation: Callable[
            [float | Fraction, float | Fraction],
            float | Fraction,
        ],
    ) -> Vector:
        """
        Creates and returns a vector that results from the element-
            wise operation of two matrices (or one vector and a number).

        Arguments
        - other: The right-hand side operand, can be either a vector or
            a number (numbers are interpreted as homogenous matrices of
            the same shape as `self`).
        - self_side_left: Whether `self` is the left operand (true), or
            the right operand (false).
        - operation: The arbitrary operation applied to two elements to
            create a single result.

        Possible Errors
        - DimensionMismatchError: If `other` is a Vector and does not
            have the required shape.

        Notes
        - The operation specified in `operation` may raise errors. These
            will not be caught by this method.
        - This is a private method not meant to be exposed.
        """
        if isinstance(other, Vector):
            if self._length != other._length:
                order = (
                    ("left", "right") if self_side_left else ("right", "left")
                )
                raise DimensionMismatchError(
                    f"{order[0]} side length {self._length} "
                    f"does not equal {order[1]} side length {other._length}"
                )
            if self_side_left:
                return Vector(
                    operation(self_item, other_item)
                    for self_item, other_item in zip(self._data, other._data)
                )
            else:
                return Vector(
                    operation(other_item, self_item)
                    for self_item, other_item in zip(self._data, other._data)
                )
        else:
            if self_side_left:
                return Vector(operation(item, other) for item in self._data)
            else:
                return Vector(operation(other, item) for item in self._data)

    def _string_format(
        self,
        max_elements: int,
        element_formatter: Callable[[Fraction], str],
    ) -> str:
        """
        Returns a "pretty" string representation of this vector.

        Arguments
        - max_elements: The maximum number of elements to print.
        - element_formatter: The operation applied to each element to
            convert it to a string.

        Notes
        - TODO: Refactor to make this more readable.
        - This is a private method not meant to be exposed.
        """

        def format_as_str(n: Fraction, idx: int) -> str:
            if idx >= max_elements:
                return "\u22EF"
            else:
                return element_formatter(n)

        return (
            f"\u27E8 "
            + ", ".join(
                (
                    format_as_str(self[element], element)
                    for element in range(min(self._length, max_elements + 1))
                )
            )
            + f" \u27E9 (size: {self._length})"
        )
