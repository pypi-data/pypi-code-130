from copy import deepcopy

from ...base import NewObject
from ..tg_objects import KeyboardButton, ReplyKeyboardMarkup
from .translations import Translations


class Keyboard(NewObject):

    def __new__(cls, *args, **kwargs):
        kb = super().__new__(cls)
        kb._buttons = []
        return kb

    def add_row(self, *buttons: KeyboardButton | str):
        self._buttons.append(list(buttons))

    def add_rows(self, *buttons: KeyboardButton | str, row_width: int = 1):
        index = 0

        while index < len(buttons):
            row = buttons[index:index + row_width]
            self._buttons.append(list(row))
            index += row_width

    def __repr__(self):
        return f'{Keyboard.__name__}({self._buttons})'

    def to_tg_object(self) -> ReplyKeyboardMarkup:
        new_buttons: list[list[KeyboardButton]] = []

        for row in self._buttons:
            new_row = []
            for btn in row:
                if isinstance(btn, (str, Translations)):
                    btn = KeyboardButton(btn)
                elif isinstance(btn, KeyboardButton):
                    btn = deepcopy(btn)
                else:
                    raise ValueError('Invalid button')

                if isinstance(btn.text, Translations):
                    btn.text = btn.text.get()

                new_row.append(btn)

            new_buttons.append(new_row)

        return ReplyKeyboardMarkup(new_buttons, resize_keyboard=True)
