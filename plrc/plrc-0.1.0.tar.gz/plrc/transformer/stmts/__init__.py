# -*- coding: utf-8 -*-

from __future__ import annotations

import ast
from typing import Any, TypeAlias, TypeVar

from lark.tree import Tree

T = TypeVar("T", bound=ast.AST)
Module: TypeAlias = ast.Name | ast.Attribute
Annotated: TypeAlias = tuple[ast.Name, ast.Name | ast.Attribute]


class StatementsParser:
    @staticmethod
    def create(kind: type[T], *args: Any, **kwargs: Any) -> T:
        return ast.fix_missing_locations(kind(*args, **kwargs))

    def annotated(self, pair: list[ast.AST | Tree]):
        if all(item for item in pair if isinstance(item, ast.AST)):
            return pair[0], pair[1]

    def import_stmt(self, name: ast.Name, module: Module) -> ast.Import:
        return self.create(
            ast.Import,
            names=[
                ast.alias(
                    name=getattr(module, "id", getattr(module, "value").id),
                    asname=name.id,
                )
            ],
        )

    def import_from_stmt(
        self, statement: tuple[ast.Name, ast.Name | ast.Attribute, ast.Name]
    ) -> ast.ImportFrom:
        module = (
            statement[2].id
            if isinstance(statement[2], ast.Name)
            else f"{statement[2].value.id}.{statement[2].attr}"
        )
        name = (
            statement[1].id
            if isinstance(statement[1], ast.Name)
            else statement[1].value
        )

        return self.create(
            ast.ImportFrom,
            module=module,
            names=[
                ast.alias(
                    name=name,
                    asname=statement[0].id,
                )
            ],
        )

    def assign_stmt(self, *statement: tuple[Annotated, ast.AST]):
        annotated_pair, value = statement[0]

        annotated_pair[0].ctx = ast.Store()
        return self.create(
            ast.AnnAssign,
            target=annotated_pair[0],
            annotation=annotated_pair[1],
            value=value,
            simple=1,
        )

    def assign_attr_stmt(
        self, statement: tuple[Tree[ast.AST], Tree[ast.AST]]
    ) -> ast.AnnAssign:
        target, annotation = statement[0].children
        value = statement[1]

        target.ctx = ast.Store()  # type: ignore
        return self.create(
            ast.AnnAssign, target=target, annotation=annotation, value=value, simple=0
        )

    def return_stmt(self, statement: list[ast.AST]) -> ast.Return:
        values = [statement[0]]
        if not isinstance(statement[0], (list, ast.AST)):
            self.recursive(statement[0], values)  # type: ignore

        if len(values) > 1:
            values = self.create(ast.Tuple, elts=values, ctx=ast.Load())
        else:
            values = values[0]

        return self.create(ast.Return, value=values)

    def yield_stmt(self, statement: list[ast.AST]) -> ast.Yield:
        self.recursive(statement[0], (values := list()))  # type: ignore

        if len(values) > 1:
            values = self.create(ast.Tuple, elts=values, ctx=ast.Load())

        return self.create(ast.Yield, value=values)

    def yield_from_stmt(self, statement: list[ast.AST]) -> ast.YieldFrom:
        self.recursive(statement[0], (values := list()))  # type: ignore

        if len(values) > 1:
            values = self.create(ast.Tuple, elts=values, ctx=ast.Load())

        return self.create(ast.YieldFrom, value=values)

    def global_stmt(self, names: list[ast.Name]) -> ast.Global:
        return self.create(ast.Global, names=[name.id for name in names])
