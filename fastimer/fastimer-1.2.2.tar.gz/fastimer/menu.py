#!/usr/bin/env python3

from vkostyanetsky import cliutils

from fastimer import view


class FastimerMenu(cliutils.Menu):
    _active_fast: dict | None = None

    def __init__(self, active_fast: dict | None = None):

        super().__init__()

        self._active_fast = active_fast

    def _print_menu(self):

        print(self._top_border())

        self._print_title()

        self._print_active_fast()

        self._print_choices()

        print(self._bottom_border())

    def _print_title(self):

        print(self._text_line("FASTING TIMER", 2))

        print(self._inner_border())

    def _print_choices(self):

        print(self._empty_line())

        for choice in self._get_choices_to_print():
            print(self._text_line(text=choice))

        print(self._empty_line())

    def _print_active_fast(self):

        if self._active_fast is not None:

            active_fast_preview = view.get(self._active_fast)

            print(self._empty_line())

            for text in active_fast_preview:
                print(self._text_line(text))

            print(self._empty_line())

            print(self._inner_border())

    def print(self):
        """
        Draws the menu.
        """
        print()

        self._print_menu()

        print(self._prompt, end="")
