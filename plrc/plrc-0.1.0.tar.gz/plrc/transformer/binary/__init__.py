# -*- coding: utf-8 -*-

from __future__ import annotations

import ast
from typing import Any, TypeVar

T = TypeVar("T", bound=ast.AST)


class BinaryParser:
    @staticmethod
    def create(kind: type[T], *args: Any, **kwargs: Any) -> T:
        return ast.fix_missing_locations(kind(*args, **kwargs))

    def addition(self, expression: tuple[ast.Expr, ast.Expr]) -> ast.BinOp:
        return self.create(
            ast.BinOp, left=expression[0], right=expression[1], op=ast.Add()
        )

    def subtraction(self, expression: tuple[ast.Expr, ast.Expr]) -> ast.BinOp:
        return self.create(
            ast.BinOp, left=expression[0], right=expression[1], op=ast.Sub()
        )

    def multiplication(self, expression: tuple[ast.Expr, ast.Expr]) -> ast.BinOp:
        return self.create(
            ast.BinOp, left=expression[0], right=expression[1], op=ast.Mult()
        )

    def division(self, expression: tuple[ast.Expr, ast.Expr]) -> ast.BinOp:
        return self.create(
            ast.BinOp, left=expression[0], right=expression[1], op=ast.Div()
        )

    def modulus(self, expression: tuple[ast.Expr, ast.Expr]) -> ast.BinOp:
        return self.create(
            ast.BinOp, left=expression[0], right=expression[1], op=ast.Mod()
        )

    def power(self, expression: tuple[ast.Expr, ast.Expr]) -> ast.BinOp:
        return self.create(
            ast.BinOp, left=expression[0], right=expression[1], op=ast.Pow()
        )
