# -*- coding: utf-8 -*-

from __future__ import annotations

import ast

from lark.lexer import Token
from lark.tree import Tree
from lark.visitors import Transformer, v_args

from .binary import BinaryParser
from .expr import ExprParser
from .functions import FunctionParser
from .stmts import StatementsParser


@v_args(inline=True)
class PolarisTransformer(
    Transformer, StatementsParser, ExprParser, BinaryParser, FunctionParser
):
    def __init__(self) -> None:
        self.nodes: list[ast.AST] = []

    def __default_token__(self, token: Token) -> ast.AST:
        kind = token.type

        if kind.endswith("LITERAL") or kind.endswith("CONST"):
            return self.constants(token)

        elif transformer := getattr(self, token.type.lower(), None):
            return transformer(token)

        raise RuntimeError(f"No callbacks given for {token.type}")
