import re
from dataclasses import dataclass

from .base import Filter
from ..context import ctx
from ..objects import CallbackButton, Translations
from ..utils import listify


@dataclass
class Button(Filter):
    value: CallbackButton | list[CallbackButton] | str | list[str] | Translations | list[Translations]

    def check_one(self, value: CallbackButton | str | Translations):
        if isinstance(value, CallbackButton):
            try:
                if not (doc_id := ctx.update.callback_query.data):
                    return False
            except AttributeError:
                return False

            btn = CallbackButton.get(doc_id)
            if not btn:
                return False
            return btn.id == self.value.id

        try:
            if not (text := ctx.update.message.text):
                return False
        except AttributeError:
            return False

        if isinstance(value, (str, Translations)):
            if isinstance(value, Translations):
                value = value.get()

            pattern = re.sub(r'\\\{.+}', '.+', re.escape(value))
            if re.fullmatch(pattern, text):
                return True

            return False

        raise ValueError('Invalid button')

    def __call__(self):
        for value in listify(self.value):
            if self.check_one(value):
                return True
        return False
