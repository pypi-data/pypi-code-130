"""Module for creating iterables using decorators."""
from __future__ import annotations

from typing import Any


def __init(self, *args) -> None:
    """Initialize the list."""
    self.args = args


def __repr(self) -> str:
    """Return a string representation of the list."""
    return f"{self.__class__.__qualname__}{self.args}"


def __iter(self) -> None:
    """Return an iterator for the list."""
    self._index = 0
    return self


def __getitem(self, index: int) -> str:
    """Return the item at the given index."""
    return self.args[index]


def __next(self) -> Any:
    """Return the next item in the list."""
    try:
        result = self.args[self._index]
    except IndexError:
        self._index = 0
        raise StopIteration

    self._index += 1
    return result


def __len(self) -> int:
    """Return the length of the list."""
    return len(self.args)


def __append(self, *args: Any) -> None:
    """Append an item to the list."""
    self.args = tuple(self.args + args)
    return self


def iterable(cls) -> type:
    """
    # Iterable.

    Create iterable classes as a decorator.

    Values are stored in the class as a tuple
    under self.args.

    ## Examples
    The bare minimum:
    ```python

    @iterable
    class Items:
        pass


    items = Items("a", "b", "c")
    ```
    You can type annotate the class like so:
    ```python
    @iterable
    class Items:
        args: str
    ```

    You can also add methods to the class:
    ```python
    @iterable
    class Items:
        args: str

        def sort(self):
            self.args = tuple(sorted(self.args))
            return self

    items = Items("b", "a", "c")
    items.sort()
    >>> Items("a", "b", "c")
    ```
    """
    setattr(cls, "__init__", __init)
    setattr(cls, "__repr__", __repr)
    setattr(cls, "__iter__", __iter)
    setattr(cls, "__next__", __next)
    setattr(cls, "__getitem__", __getitem)
    setattr(cls, "__len__", __len)
    setattr(cls, "append", __append)

    return cls
