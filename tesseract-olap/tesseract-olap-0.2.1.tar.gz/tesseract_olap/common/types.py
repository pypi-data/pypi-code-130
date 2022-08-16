from typing import Any, Dict, List, Set, Tuple, TypeVar, Union

T = TypeVar("T")

# Defines a flexible list of uncounted T items.
Array = Union[Set[T], List[T], Tuple[T, ...]]

# Defines a flexible primitive that can be used directly as a `str`.
StrLike = Union[str, int, float]

# Defines a flexible mapping of str to any value
AnyDict = Dict[str, Any]
