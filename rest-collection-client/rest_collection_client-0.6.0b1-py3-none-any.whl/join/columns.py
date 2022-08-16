from typing import NoReturn, overload

from collections_extension import Tuple

__all__ = [
    'RestCollectionJoinColumns',
]


class RestCollectionJoinColumns(Tuple[str]):
    """Container for describing join columns in join rules."""
    __slots__ = '_label', '_prefix', '_delimiter'

    def __init__(
        self,
        label: str,
        *columns: str,
        prefix: bool = True,
        delimiter: str = '.',
    ) -> None:
        super().__init__(*columns)
        self._label = label
        self._prefix = prefix
        self._delimiter = delimiter

    @property
    def label(self) -> str:
        return self._label

    @property
    def columns(self) -> tuple:
        return self._data

    @overload
    def __getitem__(self, index: int) -> str: ...

    @overload
    def __getitem__(self, index: slice) -> NoReturn: ...

    def __getitem__(self, index):
        if isinstance(index, slice):
            raise TypeError(
                f'{self.__class__.__name__} can not work with slices.',
            )

        column = super().__getitem__(index)

        if not self._prefix:
            return column

        return f'{self._label}{self._delimiter}{column}'

    @classmethod
    def just_id_column(
        cls,
        name: str,
        prefix: bool = True,
        delimiter: str = '.',
    ) -> 'RestCollectionJoinColumns':
        return cls(name, 'id', prefix=prefix, delimiter=delimiter)
