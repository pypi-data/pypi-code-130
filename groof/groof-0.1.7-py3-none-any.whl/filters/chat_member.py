from dataclasses import dataclass

from .base import Filter
from ..context import ctx
from ..utils import listify


@dataclass
class ChanMemberStatus(Filter):
    value: str | list[str]

    def __call__(self):
        if chat_member := ctx.new_chat_member:
            return chat_member.status in listify(self.value)
        return False
