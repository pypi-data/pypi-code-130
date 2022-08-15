# -*- coding: utf-8 -*-

from __future__ import annotations

import ast
from ast import fix_missing_locations as fix
from typing import ClassVar

from rply import ParserGenerator
from rply.parser import LRParser

from ..lexical import (
    ASSIGN_OPERATORS,
    BIT_OPERATORS,
    COMPARISONS,
    LITERALS,
    OPERATORS,
    STATEMENTS,
    Token,
    TokenKind,
)
from .binary import BinaryParser
from .expressions import ExprParser
from .functions import FunctionParser
from .statements import StatementsParser

PARSERS = {
    BinaryParser(),
    StatementsParser(),
    ExprParser(),
    FunctionParser(),
}


class LunarParser:
    TOKENS: ClassVar[set[str]] = (
        LITERALS
        | COMPARISONS
        | BIT_OPERATORS
        | OPERATORS
        | ASSIGN_OPERATORS
        | STATEMENTS
    ) | {
        TokenKind.Semi.name,
        TokenKind.Colon.name,
        TokenKind.Comma.name,
        TokenKind.RArrow.name,
    }

    def __init__(self) -> None:
        self.builder = ParserGenerator(LunarParser.TOKENS)

        @self.builder.production("program : stmts")
        def __program__(pieces: tuple[list[ast.AST]], /) -> list[ast.AST]:
            nodes: list[ast.AST] = []

            for node in pieces[0]:
                if isinstance(node, ast.Constant):
                    nodes.append(fix(ast.Expr(node)))
                    continue

                nodes.append(node)

            return nodes

        for parser in PARSERS:
            parser.register(self.builder)

        @self.builder.error
        def __error__(token: Token, /) -> None:
            raise ValueError(f"Error at {token}")

    def build(self) -> LRParser:
        return self.builder.build()
