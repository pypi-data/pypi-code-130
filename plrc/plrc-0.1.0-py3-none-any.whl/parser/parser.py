# -*- coding: utf-8 -*-

from __future__ import annotations

import os

from lark.lark import Lark

__all__ = ("PolarisParser",)


class PolarisParser:
    __slots__ = "parser"

    def __init__(self) -> None:
        with open(f"{os.path.dirname(__file__)}/grammar.lark", "r") as file:
            grammar = file.read()

        self.parser = Lark(
            grammar, start="program", parser="earley", propagate_positions=True
        )

    def parse(self, source: str):
        return self.parser.parse(source)
