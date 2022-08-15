"""Mapping enum module."""

# Copyright (c) 2020-2022 ObserverOfTime
#
# This software is provided 'as-is', without any express or implied
# warranty. In no event will the authors be held liable for any damages
# arising from the use of this software.
#
# Permission is granted to anyone to use this software for any purpose,
# including commercial applications, and to alter it and redistribute it
# freely, subject to the following restrictions:
#
# 1. The origin of this software must not be misrepresented; you must not
#   claim that you wrote the original software. If you use this software
#   in a product, an acknowledgment in the product documentation would be
#   appreciated but is not required.
# 2. Altered source versions must be plainly marked as such, and must not be
#   misrepresented as being the original software.
# 3. This notice may not be removed or altered from any source distribution.

from enum import Enum, EnumMeta
from typing import Any, Dict, Iterator, Tuple, Type, TypeVar

_ET = TypeVar('_ET', bound=Type[Enum])


class MappingMeta(EnumMeta):
    """Mapping enum metaclass."""
    def __iter__(cls) -> Iterator[Tuple[int, str]]:
        """
        Iterate over the values of the enum.

        Yields:
            :obj:`tuple` of :obj:`int`, :obj:`str` :

            The next tuple where the first element is the
            ``index`` of the enum instance and the second
            element is the ``label`` of the enum instance.

        Examples:
            >>> list(MappingExample)
            [(0, 'Alice'), (1, 'Bob')]
        """
        return (e.value for e in super().__iter__())

    def __call__(cls, value: Any) -> _ET:
        """
        Get an enum instance from the given value.

        Args:
            value (:obj:`~typing.Any`):
                The value to look for in the members of the enum.

        Returns:
            :obj:`~enum.Enum`: An enum instance that corresponds to the value.

        Raises:
            :obj:`ValueError`: If the given value is invalid.

        Examples:
            >>> MappingExample(0)
            <MappingExample.A: (0, 'Alice')>
            >>> MappingExample('Bob')
            <MappingExample.B: (1, 'Bob')>
        """
        if isinstance(value, int):
            value = next((v for v in cls if v[0] == value), value)
        elif isinstance(value, str):
            value = next((v for v in cls if v[1] == value), value)
        return super().__call__(value)

    @property
    def items(cls) -> Dict[str, int]:
        """
        Get a mapping of ``label``/``index`` pairs.

        Type
            :obj:`dict` of :obj:`str` to :obj:`int`

        Examples:
            >>> MappingExample.items
            {'Alice': 0, 'Bob': 1}
        """
        return {lbl: idx for idx, lbl in cls}

    @property
    def indices(cls) -> Tuple[int, ...]:
        """
        Get the indices of the enum.

        Type
            :obj:`tuple` of :obj:`int`

        Examples:
            >>> MappingExample.indices
            (0, 1)
        """
        return tuple(val[0] for val in cls)

    @property
    def labels(cls) -> Tuple[str, ...]:
        """
        Get the labels of the enum.

        Type
            :obj:`tuple` of :obj:`str`

        Examples:
            >>> MappingExample.labels
            ('Alice', 'Bob')
        """
        return tuple(val[1] for val in cls)


class MappingEnum(Enum, metaclass=MappingMeta):
    """
    Enum class which maps labels to indices.

    Attributes:
        index (int): An integer that will be used as the index.
        label (str): A string that will be used as the label.

    Examples:
        >>> class MappingExample(MappingEnum):
        ...     A = 0, 'Alice'
        ...     B = 1, 'Bob'
        >>> '%d, %s' % (MappingExample.B.index, Example.B.label)
        '1, Bob'

    .. autoattribute:: __class__
        :annotation:

        alias of :class:`enumagic.MappingMeta`

    .. automethod:: __str__() -> str
    """
    def __init__(self, index: int, label: str):
        if index in self.__class__.indices:
            raise ValueError(f'Duplicate index found: {index}')
        if label in self.__class__.labels:
            raise ValueError(f'Duplicate label found: {label}')
        self.index, self.label = index, label

    def __str__(self) -> str:
        """
        Return the instance as a string.

        Returns:
            :obj:`str`: The label of the instance.

        Examples:
            >>> str(MappingExample.A)
            'Alice'
        """
        return self.label

    def __int__(self) -> int:
        """
        Return the instance as an integer.

        Returns:
            :obj:`int`: The index of the instance.

        Examples:
            >>> int(MappingExample.A)
            0
        """
        return self.index

    def __index__(self) -> int:
        """
        Return the instance as an index.

        Returns:
            :obj:`int`: The index of the instance.

        Examples:
            >>> test = ['first', 'second']
            >>> test[MappingExample.B]
            'second'
        """
        return self.index
