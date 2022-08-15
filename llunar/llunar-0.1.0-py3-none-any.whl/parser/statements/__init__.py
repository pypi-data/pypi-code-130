# -*- coding: utf-8 -*-

from __future__ import annotations

import ast
from ast import fix_missing_locations as fix

from rply import ParserGenerator

from ...lexical import Token


class StatementsParser:
    def register(self, builder: ParserGenerator) -> None:
        production = builder.production

        @production("stmts : stmts stmt")
        @production("stmts : stmt Semi")
        @production("stmts : stmt")
        @production("stmts : expr")
        @production("stmts : empty")
        @production("stmts : const")
        @production("stmts : call")
        def __statements__(pieces: tuple[ast.AST, ...], /) -> list[ast.AST]:
            if len(pieces) == 1:
                return [pieces[0]]

            return pieces[0] + [pieces[1]]  # type: ignore

        @production("stmt : block")
        def __stblock__(pieces: tuple[list[ast.AST]], /) -> list[ast.AST]:
            return pieces[0]

        @production("stmt : assign")
        def __statement__(pieces: tuple[ast.Assign], /) -> ast.Assign:
            return pieces[0]

        @production("stmt : funcdef")
        def __sfuncdef__(pieces: tuple[ast.FunctionDef], /) -> ast.FunctionDef:
            return pieces[0]

        @production("stmt : call")
        def __sfunccall__(pieces: tuple[ast.Expr], /) -> ast.Expr:
            return pieces[0]

        @production("block : LBrace stmts RBrace")
        def __block__(pieces: tuple[Token, list[ast.AST], Token], /) -> list[ast.AST]:
            statements: list[ast.AST] = []

            for statement in pieces[1]:

                if isinstance(statement, ast.Constant):
                    statements.append(ast.Expr(value=statement))
                    continue

                statements.append(statement)

            return statements

        @production("assign : IdentLiteral OpAssign expr Semi")
        def __assign_statement__(
            pieces: tuple[Token, Token, ast.Expr, Token], /
        ) -> ast.Assign:
            return fix(
                ast.Assign(
                    targets=[ast.Name(id=pieces[0].value, ctx=ast.Store())],
                    value=pieces[2],
                )
            )
