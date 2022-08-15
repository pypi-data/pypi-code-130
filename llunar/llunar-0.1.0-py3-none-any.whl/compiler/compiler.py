# -*- coding: utf-8 -*-

from __future__ import annotations

import ast

from astpretty import pformat
from rply.parser import LRParser

from ..lexical import LunarLexer
from ..parser import LunarParser


class FileCompiler:
    __slots__ = ("dump_ast", "dump_path", "source", "lexer", "parser")

    lexer: LunarLexer
    parser: LRParser

    def __init__(self, source: str, dump_ast: bool, dump_path: None | str) -> None:
        self.dump_ast = dump_ast
        self.dump_path = dump_path
        self.source = source

    def start(self) -> None:
        self.parser = LunarParser().build()
        self.lexer = LunarLexer(self.source)

        module = ast.Module(self.parser.parse(self.lexer), type_ignores=[])
        exec(compile(module, "<ast>", "exec"))

        if self.dump_ast and self.dump_path:

            with open(self.dump_path, "w") as file:
                file.write(pformat(module) or "")
