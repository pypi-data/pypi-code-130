from dataclasses import (
    dataclass,
)
from typing import (
    Dict,
    FrozenSet,
    Optional,
    Tuple,
    Union,
)


@dataclass(frozen=True)
class _DAG:
    items: Dict[str, Tuple[FrozenSet[str], ...]]


@dataclass(frozen=True)
class DAG:
    _inner: _DAG

    def get(self, module: str) -> Optional[Tuple[FrozenSet[str], ...]]:
        return self._inner.items.get(module)


def _assert_set(items: Tuple[str, ...]) -> FrozenSet[str]:
    if len(items) == len(frozenset(items)):
        return frozenset(items)
    raise ValueError("Expected a set but got duplicated values")


def _to_set(item: Union[Tuple[str, ...], str]) -> FrozenSet[str]:
    if isinstance(item, tuple):
        return _assert_set(item)
    return _assert_set((item,))


def new_dag(raw: Dict[str, Tuple[Union[Tuple[str, ...], str], ...]]) -> DAG:
    _raw = {k: tuple(_to_set(i) for i in v) for k, v in raw.items()}
    return DAG(_DAG(_raw))
