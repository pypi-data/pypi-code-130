from dataclasses import dataclass

from .base import Filter
from ..context import ctx
from ..utils import listify


@dataclass
class ChatType(Filter):
    value: str | list[str]

    def __call__(self):
        return ctx.chat_type in listify(self.value)
