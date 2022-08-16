from inspect import getmro, isclass
from typing import Any, Hashable, Mapping, Type

from .native import Map

__all__ = [
    'ExceptionMap',
]


_MARKER = object()


def _is_exception(value: Any) -> bool:
    return isclass(value) and issubclass(value, Exception)


class ExceptionMap(Map[Type[Exception], Any]):
    """Exception map with hierarchy inheritance checking."""
    __slots__ = ('_default_value',)

    def __init__(
        self,
        data: Mapping[Type[Exception], Any],
        default_value: Any = None,
    ) -> None:
        # Assert data keys
        assert all(
            map(
                _is_exception, data,
            ),
        ), f'All keys of {ExceptionMap.__name__!r} must be subclasses ' \
           f'of {Exception.__name__!r} class.'

        super().__init__(data)
        self._default_value = default_value

    def __getitem__(self, key: Type[Exception]) -> Any:

        if not isinstance(key, Hashable):
            # Emulate Map hashable type checking.
            raise TypeError(
                f'unhashable type: {type(key).__name__!r}',
            )

        if not _is_exception(key):
            raise KeyError(key)

        data = self._data

        for cls in getmro(key):
            if cls in data:
                return data[cls]

            if cls is Exception:
                raise KeyError(key)

    def get(
        self,
        key: Type[Exception],
        default: Any = _MARKER,
    ) -> Any:

        if default is _MARKER:
            default = self._default_value

        return super().get(key, default)
