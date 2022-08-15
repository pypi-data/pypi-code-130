"""Iterable enum module."""

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
from typing import Any, Iterator, Tuple, Type, TypeVar

_VT = TypeVar('_VT')
_ET = TypeVar('_ET', bound=Type[Enum])


class IterMeta(EnumMeta):
    """Iterable enum metaclass."""
    def __iter__(cls) -> Iterator[Tuple[str, _VT]]:
        """
        Iterate over the entries of the enum.

        Yields:
            :obj:`tuple` of :obj:`str`, :obj:`object` :

            The next tuple where the first element is the
            ``name`` of the enum instance and the second
            element is the ``value`` of the enum instance.

        Examples:
            >>> it = iter(IterExample)
            >>> next(it)
            ('A', 'Alice')
        """
        return ((e.name, e.value) for e in super().__iter__())

    def __contains__(cls, item: Any) -> bool:
        """
        Check whether the enum contains a certain item

        Args:
            item (:obj:`~typing.Any`): A string or enum instance.

        Returns:
            :obj:`bool`:

            ``True`` if the enum has a member that
            matches the given item, ``False`` otherwise.

        Examples:
            >>> 'B' in IterExample
            True
            >>> 'C' in IterExample
            False
        """
        if isinstance(item, str):
            return item in cls.__members__.keys()
        if not isinstance(item, Enum):
            return False
        return super().__contains__(item)


class IterEnum(Enum, metaclass=IterMeta):
    """
    Enum class that can be used as an iterable.

    .. autoattribute:: __class__
        :annotation:

        alias of :class:`enumagic.IterMeta`

    Examples:
        >>> class IterExample(IterEnum):
        ...     A = 'Alice'
        ...     B = 'Bob'
        >>> dict(IterExample)
        {'A': 'Alice', 'B': 'Bob'}
    """
