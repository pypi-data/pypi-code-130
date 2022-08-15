from typing import Any, Callable


def is_empty(value: Any) -> bool:
    """
    Returns True if *value* is None or has __len__ defined and has length of 0,
    False otherwise.
    """
    return value is None or (hasattr(value, "__len__") and len(value) == 0)


def is_mutable(value: Any) -> bool:
    """
    Returns True if *value* is mutable, False otherwise.
    """
    return isinstance(value, (list, dict, set))


def call_or_return_value(a: Any | Callable, *args, **kwargs) -> Any:
    """
    If *a* is callable, call it with *args* and *kwargs*, otherwise return *a*.
    """
    if callable(a):
        return a(*args, **kwargs)

    return a
