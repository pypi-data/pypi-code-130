# -*- coding: utf-8 -*-

from __future__ import annotations

import ast
from typing import Any, TypeVar

from lark.tree import Tree

T = TypeVar("T", bound=ast.AST)


class FunctionParser:
    @staticmethod
    def create(kind: type[T], *args: Any, **kwargs: Any) -> T:
        return ast.fix_missing_locations(kind(*args, **kwargs))

    @staticmethod
    def recursive(tree: Tree, append_to: list[ast.AST]) -> list[ast.AST]:
        for node in tree.iter_subtrees():

            for child in node.children:
                if isinstance(child, Tree):
                    return FunctionParser.recursive(child, append_to)

                if not isinstance(child, list):
                    append_to.append(child)
                    continue

                append_to.extend(child)

        return append_to

    def declare_func(self, statement: list) -> ast.FunctionDef:
        returns: ast.Name | ast.Constant = statement[2]
        args: list[ast.arg] = []

        for child in statement[1].children:
            args.append(
                ast.arg(child.children[0][0].id, annotation=child.children[0][1])
            )

        instructions: list[ast.AST] = []
        for instruction in statement[3:]:

            if isinstance(instruction, Tree):
                FunctionParser.recursive(instruction, instructions)
                continue

            elif isinstance(instruction, ast.AST):
                if isinstance(instruction, ast.expr):
                    instruction = self.create(ast.Expr, instruction)

                instructions.append(instruction)

        for index, expr_stmt in enumerate(instructions):

            if isinstance(expr_stmt, ast.expr):
                instructions[index] = self.create(ast.Expr, expr_stmt)

        arguments = self.create(
            ast.arguments,
            args=args,
            posonlyargs=[],
            kwonlyargs=[],
            kw_defaults=[],
            defaults=[],
        )

        return self.create(
            ast.FunctionDef,
            name=statement[0].id,
            args=arguments,
            body=instructions,
            decorator_list=[],
            returns=returns,
        )

    def func_call(self, statement: tuple[ast.Name | ast.Attribute, Tree]) -> ast.Call:
        FunctionParser.recursive(statement[1], (arguments := list()))
        return self.create(ast.Call, func=statement[0], args=arguments, keywords=[])
