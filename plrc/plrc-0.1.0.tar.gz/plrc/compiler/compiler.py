# -*- coding: utf-8 -*-

from __future__ import annotations

import ast

from astpretty import pformat

from ..parser import PolarisParser
from ..transformer import PolarisTransformer


class FileCompiler:
    __slots__ = ("dump_ast", "dump_path", "source", "lexer", "parser")

    parser: PolarisParser

    def __init__(self, source: str, dump_ast: bool, dump_path: None | str) -> None:
        self.dump_ast = dump_ast
        self.dump_path = dump_path
        self.source = source

    def start(self) -> None:
        tree = PolarisParser().parse(self.source)
        tree = PolarisTransformer().transform(tree)

        body = list(tree.scan_values(lambda node: isinstance(node, ast.AST)))
        module = ast.Module(body, type_ignores=[])

        for index, node in enumerate(module.body):

            if isinstance(node, (ast.expr, ast.Call)):
                module.body[index] = ast.fix_missing_locations(ast.Expr(node))

            # Temporary fix for single stmt exprs (do this automatically later in visitors)

        exec(compile(module, "<compiled>", "exec"))
        if self.dump_ast and self.dump_path:

            with open(self.dump_path, "w") as file:
                file.write(pformat(module) or "")
