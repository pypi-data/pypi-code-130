from __future__ import annotations

from dataclasses import dataclass
import os

from simple_terminal_control.util.terminal import (
    assert_empty_read,
    read_chars_until,
    write_csi,
    setup,
)


@dataclass(frozen=True, kw_only=True)
class TerminalPositionDelta:
    drow: int
    dcol: int

    def __add__(self, other: TerminalPositionDelta):
        return TerminalPositionDelta(drow=self.drow + other.drow, dcol=self.dcol + other.dcol)

    def __sub__(self, other: TerminalPositionDelta):
        return TerminalPositionDelta(drow=self.drow - other.drow, dcol=self.dcol - other.dcol)

    def __mul__(self, n: int):
        return TerminalPositionDelta(drow=self.drow * n, dcol=self.dcol * n)

    def __idiv__(self, n: int):
        return TerminalPositionDelta(drow=self.drow // n, dcol=self.dcol // n)


_MAX_COL, _MAX_ROW = os.get_terminal_size()


@dataclass(frozen=True, kw_only=True)
class TerminalPosition:
    row: int
    col: int

    def __post_init__(self):
        row = min(max(self.row, 1), _MAX_ROW)
        col = min(max(self.col, 1), _MAX_COL)
        object.__setattr__(self, "row", row)
        object.__setattr__(self, "col", col)

    @classmethod
    def get_cursor(cls):
        with setup(report_mouse=False):
            assert_empty_read()
            write_csi("6n", flush=True)
            s = read_chars_until("R")
            assert s[:2] == "\x1b[" and s[-1] == "R"
            row, col = map(int, s[2:-1].split(";"))
            return cls(row=row, col=col)

    def set_cursor(self):
        write_csi(f"{self.row};{self.col}H", flush=True)

    def add_chars(self, n: int):
        col = self.col + n
        row = self.row + (col // MAX_POSITION.col)
        col = col % MAX_POSITION.col
        return self.__class__(row=row, col=col)

    def next_line(self):
        return self.__class__(row=self.row + 1, col=1)

    def __add__(self, other: TerminalPositionDelta):
        return self.__class__(row=self.row + other.drow, col=self.col + other.dcol)

    def __sub__(self, other: TerminalPosition):
        return TerminalPositionDelta(drow=self.row - other.row, dcol=self.col - other.col)


MAX_POSITION = TerminalPosition(row=_MAX_ROW, col=_MAX_COL)
