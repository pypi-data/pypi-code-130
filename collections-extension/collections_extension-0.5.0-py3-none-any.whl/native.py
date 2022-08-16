from types import MappingProxyType
from typing import Any, Hashable, Iterator, Mapping, MutableMapping, \
    MutableSequence, MutableSet, Optional, Sequence, TypeVar

__all__ = [
    'Tuple',
    'List',
    'Map',
    'Dict',
    'Set',
]


_AnyType = TypeVar('_AnyType', bound=Any)
_HashableType = TypeVar('_HashableType', bound=Hashable)


class _RepresentableMixin:
    __slots__ = '_data', '__weakref__'

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} data={self._data!r}>'

    def __bool__(self) -> bool:
        return bool(self._data)


class Tuple(
    _RepresentableMixin,
    Sequence[_AnyType],
):
    """Tuple-like data wrapper."""
    __slots__ = ()

    def __init__(self, *data: _AnyType) -> None:
        self._data = data

    def __getitem__(self, index: int) -> _AnyType:
        return self._data[index]

    def __len__(self) -> int:
        return len(self._data)


# noinspection PyUnresolvedReferences
Tuple.register(tuple)


class List(
    _RepresentableMixin,
    MutableSequence[_AnyType],
):
    """List-like data wrapper."""
    __slots__ = ()

    def __init__(
        self,
        data: Optional[MutableSequence[_AnyType]] = None,
    ) -> None:
        if data is None:
            data = []
        self._data = data

    def __getitem__(self, index: int) -> _AnyType:
        return self._data[index]

    def __len__(self) -> int:
        return len(self._data)

    def __setitem__(self, index: int, value: _AnyType) -> None:
        self._data[index] = value

    def insert(self, index: int, value: _AnyType) -> None:
        self._data.insert(index, value)

    def __delitem__(self, index: int) -> None:
        del self._data[index]


# noinspection PyUnresolvedReferences
List.register(list)


class Map(
    _RepresentableMixin,
    Mapping[_HashableType, _AnyType],
):
    """Immutable-dist-like data wrapper."""
    __slots__ = ()

    def __init__(self, data: Mapping[_HashableType, _AnyType]) -> None:
        self._data = data

    def __iter__(self) -> Iterator[_HashableType]:
        return iter(self._data)

    def __getitem__(self, key: _HashableType) -> _AnyType:
        return self._data[key]

    def __len__(self) -> int:
        return len(self._data)


# noinspection PyUnresolvedReferences
Map.register(MappingProxyType)


class Dict(
    Map[_HashableType, _AnyType],
    MutableMapping[_HashableType, _AnyType],
):
    """Dict-like data wrapper."""
    __slots__ = ()

    def __init__(
        self,
        data: Optional[MutableMapping[_HashableType, _AnyType]] = None,
    ) -> None:
        if data is None:
            data = {}
        super().__init__(data)

    def __setitem__(self, key: _HashableType, value: _AnyType) -> None:
        self._data[key] = value

    def __delitem__(self, key: _HashableType) -> None:
        del self._data[key]


# noinspection PyUnresolvedReferences
Dict.register(dict)


class Set(
    _RepresentableMixin,
    MutableSet[_HashableType],
):
    """Set-like data wrapper."""
    __slots__ = ()

    def __init__(
        self,
        data: Optional[MutableSet[_HashableType]] = None,
    ) -> None:
        if data is None:
            data = set()
        self._data = data

    def add(self, value: _HashableType) -> None:
        self._data.add(value)

    def __iter__(self) -> Iterator[_HashableType]:
        return iter(self._data)

    def __len__(self) -> int:
        return len(self._data)

    def discard(self, value: _HashableType) -> None:
        self._data.discard(value)

    def __contains__(self, value: _HashableType) -> bool:
        return value in self._data


# noinspection PyUnresolvedReferences
Set.register(set)
