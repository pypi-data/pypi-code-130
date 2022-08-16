from functools import partial
from typing import Any, Callable, Dict, cast

from collections_extension import Map

__all__ = [
    'RestCollectionRenameFactory',
]


class RestCollectionRenameFactory(Map[str, Callable[[str], str]]):
    __slots__ = ('_delimiter',)

    def __init__(self, delimiter: str = '.') -> None:
        super().__init__({})
        self._delimiter = delimiter

    def _rename(self, label: str, suffix: str) -> str:
        return f'{label}{self._delimiter}{suffix}'

    def __getitem__(self, key: str) -> Callable[[str], str]:
        data = cast(Dict[str, Callable[[str], str]], self._data)
        if key not in data:
            data[key] = partial(self._rename, key)
        return super().__getitem__(key)

    def __contains__(self, key: Any) -> bool:
        return key in self._data
