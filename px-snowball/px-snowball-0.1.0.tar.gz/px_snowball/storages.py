from typing import Any, List, Optional


Value = Any
EMPTY = object()


class Storage:
    is_empty: bool

    def __init__(self, initial: Optional[Value] = EMPTY):
        if initial is not EMPTY:
            self.add(initial)

    def add(self, value: Value):
        raise NotImplementedError()

    def get(self) -> List[Value]:
        raise NotImplementedError()

    def clear(self):
        raise NotImplementedError()


class InMemStorage(Storage):
    values: List[Value]

    def __init__(self, initial: Optional[Value] = EMPTY):
        self.clear()

        super().__init__(initial)

    def add(self, value: Value):
        self.values.append(value)

    def get(self) -> List[Value]:
        return self.values

    def clear(self):
        self.values = []

    @property
    def is_empty(self) -> bool:
        return len(self.values) == 0
