from dataclasses import (
    dataclass,
)
from typing import (
    Dict,
    FrozenSet,
    NoReturn,
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

    def get_children(self, module: str) -> FrozenSet[str]:
        items = self.get(module)
        if items:
            item_set = set()
            for i in items:
                for x in i:
                    if x not in item_set:
                        item_set.add(x)
                    else:
                        raise Exception(
                            f"Dag must not contain duplicated child modules i.e. {module + '.' + x}"
                        )
            return frozenset(item_set)
        return frozenset()


def _assert_set(items: Tuple[str, ...]) -> FrozenSet[str]:
    if len(items) == len(frozenset(items)):
        return frozenset(items)
    raise ValueError("Expected a set but got duplicated values")


def _to_set(item: Union[Tuple[str, ...], str]) -> FrozenSet[str]:
    if isinstance(item, tuple):
        return _assert_set(item)
    return _assert_set((item,))


def new_dag(
    raw: Dict[str, Tuple[Union[Tuple[str, ...], str], ...]]
) -> Union[DAG, NoReturn]:
    _raw = {k: tuple(_to_set(i) for i in v) for k, v in raw.items()}
    return DAG(_DAG(_raw))
