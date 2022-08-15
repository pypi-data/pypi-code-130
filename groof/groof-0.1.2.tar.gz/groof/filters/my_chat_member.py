from dataclasses import dataclass

from .base import Filter
from ..context import ctx


@dataclass
class MyChatMember(Filter):
    def __call__(self):
        try:
            return bool(ctx.update.my_chat_member)
        except AttributeError:
            return False
