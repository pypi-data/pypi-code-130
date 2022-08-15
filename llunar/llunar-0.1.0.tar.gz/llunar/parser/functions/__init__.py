# -*- coding: utf-8 -*-

from __future__ import annotations

import ast
from ast import fix_missing_locations as fix

from rply import ParserGenerator

from ...lexical import Token


class FunctionParser:
    def register(self, builder: ParserGenerator) -> None:
        production = builder.production

        @production("empty : ")
        def __empty__(_: list[Token], /) -> None:
            return None

        @production("types : const")
        @production("types : var")
        def __types__(
            pieces: tuple[ast.Constant] | tuple[ast.Name], /
        ) -> ast.Constant | ast.Name:
            return pieces[0]

        @production("params : param")
        @production("params : empty")
        def __parameters__(pieces: list[ast.AST], /) -> list[ast.AST]:
            return pieces

        @production("params : param Comma params")
        def __mult_parameters__(
            pieces: tuple[ast.arg, Token, list[ast.arg]], /
        ) -> list[ast.arg]:
            parameters: list[ast.arg] = []

            for parameter in pieces:
                if isinstance(parameter, list):
                    parameters.extend(
                        filter(lambda p: isinstance(p, ast.arg), parameter)
                    )

                if isinstance(parameter, ast.arg):
                    parameters.append(parameter)

            return parameters

        @production("param : var Colon types")
        def __parameter__(pieces: tuple[ast.Name, Token, ast.AST], /) -> ast.arg:
            return fix(ast.arg(arg=pieces[0].id, annotation=pieces[2]))

        @production("funcdef : var Colon Colon LParen params RParen RArrow types block")
        def __funcdef__(
            pieces: tuple[
                ast.Name,
                Token,
                Token,
                Token,
                list[ast.arg],
                Token,
                Token,
                ast.Constant | ast.Name,
                list[ast.AST],
            ],
            /,
        ) -> ast.FunctionDef:
            return fix(
                ast.FunctionDef(
                    name=pieces[0].id,
                    body=pieces[8],
                    decorator_list=[],
                    returns=pieces[7],
                    args=ast.arguments(
                        args=pieces[4],
                        posonlyargs=[],
                        kwonlyargs=[],
                        kw_defaults=[],
                        defaults=[],
                    ),
                )
            )

        @production("call : var LParen args RParen Semi")
        def __funccall__(pieces: tuple[ast.Name, Token, list[ast.arg]]) -> ast.Expr:
            return fix(ast.Expr(ast.Call(func=pieces[0], args=pieces[2], keywords=[])))

        @production("args : arg")
        @production("args : empty")
        def __arguments__(pieces: list[ast.AST], /) -> list[ast.AST]:
            return pieces

        @production("args : arg Comma args")
        def __mult_arguments__(
            pieces: tuple[ast.arg, Token, list[ast.AST]], /
        ) -> list[ast.AST]:
            arguments: list[ast.AST] = []
            for argument in pieces:

                if isinstance(argument, list):
                    arguments.extend(filter(lambda a: isinstance(a, ast.AST), argument))

                if isinstance(argument, ast.AST):
                    arguments.append(argument)

            return arguments

        @production("arg : expr")
        @production("arg : var")
        def __argument__(pieces: tuple[ast.AST], /) -> ast.AST:
            return fix(pieces[0])
