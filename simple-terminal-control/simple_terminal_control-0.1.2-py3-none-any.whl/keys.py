from __future__ import annotations
from abc import ABC
from dataclasses import KW_ONLY, dataclass
from typing import TypeAlias

from typing import Iterator

from simple_terminal_control._raw_keys import (
    Delete,
    Tab,
    Enter,
    Arrow,
    Mouse,
    raw_key_from_sequence,
)
from simple_terminal_control.position import TerminalPosition
from simple_terminal_control.util.terminal import read_chars, setup


@dataclass(frozen=True)
class _MouseBase(ABC):
    position: TerminalPosition
    _: KW_ONLY
    shift: bool
    ctrl: bool


@dataclass(frozen=True, kw_only=True)
class Click(_MouseBase):
    secondary: bool


@dataclass(frozen=True, kw_only=True)
class Drag(_MouseBase):
    secondary: bool
    origin: TerminalPosition


@dataclass(frozen=True, kw_only=True)
class Scroll(_MouseBase):
    down: bool


Key: TypeAlias = Delete | Tab | Enter | Arrow | Click | Drag | Scroll


_ESC = "\x1b"


def _raw_key_stream():
    while True:
        chars = read_chars()
        sequences = chars.split(_ESC)
        for seq in sequences:
            if seq == "":
                continue
            if len(sequences) > 1:
                seq = _ESC + seq

            if len(seq) != 1 or ord(seq) < 32 or 126 < ord(seq):
                if (raw_key := raw_key_from_sequence(seq)) is not None:
                    yield raw_key
                    continue
                if seq.startswith(_ESC):
                    continue
                if any(ord(c) < 32 for c in seq):
                    seq = "".join(c for c in seq if ord(c) >= 32)
            yield seq


def _make_scroll(mouse: Mouse):
    assert mouse.button.is_scroll
    return Scroll(
        position=mouse.position,
        shift=mouse.shift,
        ctrl=mouse.cmd,
        down=mouse.button == Mouse.Button.SCROLL_DOWN,
    )


def _make_click(mouse: Mouse):
    assert mouse.button.is_clickable
    return Click(
        position=mouse.position,
        shift=mouse.shift,
        ctrl=mouse.cmd,
        secondary=mouse.button == Mouse.Button.SECONDARY,
    )


def _make_drag(mouse: Mouse, origin: TerminalPosition):
    return Drag(
        position=mouse.position,
        shift=mouse.shift,
        ctrl=mouse.cmd,
        secondary=mouse.button == Mouse.Button.SECONDARY,
        origin=origin,
    )


def _key_stream():
    last_mouse_presses: dict[Mouse.Button, Mouse] = {}
    for raw_key in _raw_key_stream():
        match raw_key:
            case Mouse():
                if raw_key.button.is_scroll:
                    yield _make_scroll(raw_key)
                    continue

                if not raw_key.release:
                    last_mouse_presses[raw_key.button] = raw_key
                    continue

                if (last_press := last_mouse_presses.pop(raw_key.button, None)) is not None:
                    if last_press.position == raw_key.position:
                        yield _make_click(raw_key)
                    else:
                        yield _make_drag(raw_key, last_press.position)
            case _:
                yield raw_key


def get_keys(report_mouse: bool = False) -> Iterator[Key | str]:
    with setup(report_mouse):
        for key in _key_stream():
            yield key
