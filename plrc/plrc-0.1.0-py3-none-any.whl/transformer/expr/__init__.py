# -*- coding: utf-8 -*-

from __future__ import annotations

import ast
from functools import partial
from typing import Any, TypeVar

from lark.lexer import Token
from lark.tree import Tree

T = TypeVar("T", bound=ast.AST)


class ExprParser:
    @staticmethod
    def create(kind: type[T], *args: Any, **kwargs: Any) -> T:
        return ast.fix_missing_locations(kind(*args, **kwargs))

    @staticmethod
    def recursive(tree: Tree, append_to: list[ast.AST]) -> list[ast.AST]:
        for node in tree.iter_subtrees():

            for child in node.children:
                if isinstance(child, Tree):
                    return ExprParser.recursive(child, append_to)

                if not isinstance(child, list):
                    append_to.append(child)
                    continue

                append_to.extend(child)

        return append_to

    def atomic(self, atomic: ast.Name | ast.Constant) -> ast.Name | ast.Constant:
        return atomic

    def identifier(self, token: Token) -> ast.Name:
        return self.create(ast.Name, id=token.value, ctx=ast.Load())

    def attr(self, attributes: list[ast.Name]):
        attribute = self.create(
            ast.Attribute, value=attributes[0], attr=attributes[1].id, ctx=ast.Load()
        )

        for other in attributes[2:]:
            attribute = self.create(
                ast.Attribute, value=attribute, attr=other.id, ctx=ast.Load()
            )

        return attribute

    def constants(self, token: Token) -> ast.Constant:
        create: partial[Any] = partial(self.create, kind=ast.Constant)

        match token.type:
            case "STRING_LITERAL":
                return create(value=token.value)
            case "INTEGER_LITERAL":
                return create(value=int(token.value))
            case "FLOAT_LITERAL":
                return create(value=float(token.value))
            case "HEX_LITERAL":
                return create(value=int(token.value, 16))
            case "OCTAL_LITERAL":
                return create(value=int(token.value, 8))
            case "BINARY_LITERAL":
                return create(value=int(token.value, 2))
            case "BOOLEAN_CONST":
                return create(value=True if token.value == "True" else False)
            case "NULL_CONST":
                return create(value=None)

        assert False  # Un-reachable

    def paren_expr(self, tree: tuple[Tree[ast.AST]]) -> list[ast.AST]:
        instructions: list[ast.AST] = []

        for node in tree[0].iter_subtrees():
            ExprParser.recursive(node, instructions)

        return instructions

    def brack_expr(self, tree: tuple[Tree]) -> list[ast.AST]:
        instructions: list[ast.AST] = []

        for node in tree[0].iter_subtrees():
            ExprParser.recursive(node, instructions)

        return instructions

    def brace_expr(self, tree: tuple[Tree]) -> list[ast.AST]:
        instructions: list[ast.AST] = []

        for node in tree[0].iter_subtrees():
            ExprParser.recursive(node, instructions)

        return instructions
