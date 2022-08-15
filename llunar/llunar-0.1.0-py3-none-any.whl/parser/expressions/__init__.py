# -*- coding: utf-8 -*-

from __future__ import annotations

import ast
from ast import fix_missing_locations as fix
from typing import Any

from rply import ParserGenerator

from ...lexical import Token, TokenKind

CONSTANTS_MAPPING: dict[str, Any] = {
    "None": None,
    "True": True,
    "False": False,
    "...": ...,
}


class ExprParser:
    def register(self, builder: ParserGenerator) -> None:
        production = builder.production

        @production("expr : StrLiteral")
        @production("expr : IntLiteral")
        @production("const : IdentLiteral")
        def __produce_constants__(pieces: tuple[Token], /) -> ast.Constant:
            if constant := CONSTANTS_MAPPING.get(pieces[0].value):
                return fix(ast.Constant(value=constant))

            return fix(
                ast.Constant(
                    value=[str, int][pieces[0].kind is TokenKind.IntLiteral](
                        pieces[0].value
                    )
                )
            )

        @production("var : IdentLiteral")
        def __produce_variables__(pieces: tuple[Token]) -> ast.Name:
            return fix(ast.Name(id=pieces[0].value, ctx=ast.Load()))

        @production("expr : LParen expr RParen")
        def __parenthesis__(pieces: tuple[Token, ast.AST, Token]) -> ast.AST:
            return pieces[1]
