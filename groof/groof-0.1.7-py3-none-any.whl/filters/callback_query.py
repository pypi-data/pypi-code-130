from dataclasses import dataclass

from .base import Filter
from ..context import ctx
from ..utils import listify


@dataclass
class CallbackQuery(Filter):
    data: str | list[str] = None

    def __call__(self):
        try:
            if not (data := ctx.update.callback_query.data):
                return False
        except AttributeError:
            return False

        if self.data is None:
            return True

        return data in listify(self.data)
