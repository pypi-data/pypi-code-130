# -*- coding: utf-8 -*-

from __future__ import annotations

import ast
from ast import fix_missing_locations as fix

from rply import ParserGenerator

from ...lexical import Token


class BinaryParser:
    def register(self, builder: ParserGenerator) -> None:
        production = builder.production

        @production("math : OpAdd")
        def __add__(_: tuple[Token], /) -> ast.Add:
            return ast.Add()

        @production("math : OpSub")
        def __sub__(_: tuple[Token], /) -> ast.Sub:
            return ast.Sub()

        @production("math : OpMult")
        def __mult__(_: tuple[Token], /) -> ast.Mult:
            return ast.Mult()

        @production("math : OpDiv")
        def __div__(_: tuple[Token], /) -> ast.Div:
            return ast.Div()

        @production("math : OpFloorDiv")
        def __fdiv__(_: tuple[Token], /) -> ast.FloorDiv:
            return ast.FloorDiv()

        @production("math : OpMod")
        def __mod__(_: tuple[Token], /) -> ast.Mod:
            return ast.Mod()

        @production("expr : expr math expr")
        def __binary_expr__(pieces: tuple[ast.AST, ast.AST, ast.AST]) -> ast.Expr:
            return fix(
                ast.Expr(value=ast.BinOp(left=pieces[0], op=pieces[1], right=pieces[2]))
            )
