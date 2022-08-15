from dataclasses import dataclass

from .base import Filter
from ..context import ctx
from ..utils import listify


@dataclass
class UserId(Filter):
    value: int | list[int]

    def __call__(self):
        return ctx.user_id in listify(self.value)
