from .callback_button import CallbackButton
from .url_button import UrlButton
from ...base import NewObject
from ..tg_objects import InlineKeyboardMarkup, InlineKeyboardButton
from ..new.translations import Translations

BUTTONS = '__buttons'


class InlineKeyboard(NewObject):

    def __new__(cls, *args, **kwargs):
        kb = super().__new__(cls)
        kb._buttons = []
        return kb

    def add_row(self, *buttons: CallbackButton | UrlButton):
        self._buttons.append(list(buttons))

    def add_rows(self, *buttons: CallbackButton | UrlButton):
        self._buttons.extend([btn] for btn in buttons)

    def __repr__(self):
        return f'{InlineKeyboard.__name__}({self._buttons})'

    def to_tg_object(self) -> InlineKeyboardMarkup:
        new_buttons: list[list[InlineKeyboardButton]] = []

        for row in self._buttons:
            new_row = []
            for btn in row:

                text = btn.text
                if isinstance(text, Translations):
                    text = text.get()

                if isinstance(btn, CallbackButton):
                    new_btn = InlineKeyboardButton(text, callback_data=btn.doc_id)
                elif isinstance(btn, UrlButton):
                    new_btn = InlineKeyboardButton(text, url=btn.url)
                else:
                    raise ValueError('Invalid button')

                new_row.append(new_btn)

            new_buttons.append(new_row)

        return InlineKeyboardMarkup(new_buttons)
