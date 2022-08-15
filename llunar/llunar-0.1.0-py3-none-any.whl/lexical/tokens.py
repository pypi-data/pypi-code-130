# -*- coding: utf-8 -*-

from __future__ import annotations

import enum


class TokenKind(enum.Enum):
    """Token type enumerations.
    The values' of each enumeration is the token's REGEX pattern.
    """

    FuncDef = r"func"

    StrLiteral = r"['\"](.*?)['\"]"
    IdentLiteral = r"\.\.\.|[a-zA-Z_][0-9a-zA-Z_]*"

    IntLiteral = r"[-]?(?<!\.)\b[0-9]+\b(?!\.[0-9])"
    FloatLiteral = r"[-]?(?=\d*[.eE])(?=.?\d)\d*.?\d*(?:[eE][+-]?\d+)?"

    HexLiteral = r"0[xX][0-9a-fA-F]+"
    OctalLiteral = r"0o[1-7][0-7]+"
    BinaryLiteral = r"0b[0-1]+"

    OpAdd = r"\+"
    OpSub = r"-(?!>)"
    OpMult = r"\*"
    OpDiv = r"/(?!/)"
    OpFloorDiv = r"//"
    OpMod = r"%"

    OpAssign = r"="
    OpAIncrement = r"\+="
    OpADecrement = r"\-="
    OpAMultiply = r"\*="
    OpADivide = r"\/="
    OpAModulo = "r%="

    OpAFloorDiv = r"\/\/="
    OpAExponential = r"\*\*="

    OpABitAnd = r"&="
    OpABitOr = r"\|="
    OpABitXOR = r"\^="
    OpABitRShift = r">>="
    OpABitLShift = r"<<="

    BitAnd = r"&"
    BitOr = r"\|"
    BitXOR = r"\^"
    BitRShift = r">>"
    BitLShift = r"<<"

    CmpEqual = r"=="
    CmpNotEqual = r"!="
    CmpGT = r">"
    CmpLT = r"<"
    CmpGTE = r">="
    CmpLTE = r"<="

    Semi = r";"
    Colon = r":"
    Comma = r","
    RArrow = r"->"

    LParen = r"\("
    RParen = r"\)"
    LBrace = r"\{"
    RBrace = r"\}"
    LBrack = r"\["
    RBrack = r"\]"


LITERALS: set[str] = {kind.name for kind in TokenKind if kind.name.endswith("Literal")}
COMPARISONS: set[str] = {kind.name for kind in TokenKind if kind.name.startswith("Cmp")}
STATEMENTS: set[str] = {
    kind.name
    for kind in (
        TokenKind.FuncDef,
        TokenKind.LParen,
        TokenKind.RParen,
        TokenKind.LBrace,
        TokenKind.RBrace,
        TokenKind.LBrack,
        TokenKind.RBrack,
    )
}

BIT_OPERATORS: set[str] = {
    kind.name for kind in TokenKind if kind.name.startswith("Bit")
}

ASSIGN_OPERATORS: set[str] = {
    kind.name for kind in TokenKind if kind.name.startswith("OpA")
} - {TokenKind.OpAdd.name}

OPERATORS = {
    name
    for name in (
        TokenKind.OpAdd.name,
        TokenKind.OpSub.name,
        TokenKind.OpMult.name,
        TokenKind.OpDiv.name,
        TokenKind.OpFloorDiv.name,
        TokenKind.OpMod.name,
    )
}


class Token:
    __slots__ = ("kind", "value", "pos")

    def __init__(self, kind: TokenKind, value: str, pos: int) -> None:
        self.kind = kind
        self.value = value
        self.pos = pos

    gettokentype = lambda self: self.kind.name
    getsourcepos = lambda self: self.pos

    def __repr__(self) -> str:
        return f"<Token position={self.pos}, kind={self.kind}, value={self.value}>"

    __str__ = __repr__
