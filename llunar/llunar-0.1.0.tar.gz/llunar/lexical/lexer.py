# -*- coding: utf-8 -*-

from __future__ import annotations

import re
from typing import ClassVar

from .tokens import Token, TokenKind


class LunarLexer:
    REGEX_PATTERNS: ClassVar[list[str]] = list()

    for kind, pattern in TokenKind.__members__.items():
        REGEX_PATTERNS.append(f"(?P<{kind}>{pattern.value})")

    PATTERN: re.Pattern[str] = re.compile("|".join(REGEX_PATTERNS))

    def __init__(self, source: str) -> None:
        self.source = source
        self.max_length = len(source)
        self.index = 0

        self.line_no = 1
        self.col_no = 1

    def update(self, matched: re.Match[str]) -> None:
        start, last = matched.start(), self.source.rfind("\n", 0, matched.start())

        offset = start + 1 if last == -1 else start - last
        self.col_no = offset

    def scan(self) -> None | Token:
        if self.index >= len(self.source):
            return None

        while self.source[self.index].isspace():
            current = self.source[self.index]
            self.index += 1

            if current == "\n":
                self.line_no += 1

            if self.index == len(self.source):
                return None

        if matched := LunarLexer.PATTERN.match(self.source, self.index):
            current, self.index, = (
                self.index,
                matched.end(),
            )
            self.update(matched)

            if group := matched.lastgroup:
                return Token(TokenKind[group], matched.group(group), current)

        raise RuntimeError(
            f"Un-expected token reached: `{self.source[self.index]}`",
            f"line: {self.line_no} column: {self.col_no}",
        ) from None

    def __iter__(self) -> LunarLexer:
        return self

    def __next__(self) -> None | Token:
        while token := self.scan():
            return token

        raise StopIteration("END-OF-STREAM")
