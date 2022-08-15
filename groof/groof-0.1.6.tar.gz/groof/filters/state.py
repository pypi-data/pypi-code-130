from dataclasses import dataclass

from .base import Filter
from ..context import ctx
from ..utils import listify


@dataclass
class State(Filter):
    value: str | list[str] = None

    def __call__(self):
        return self.value == '*' or ctx.state in listify(self.value)
