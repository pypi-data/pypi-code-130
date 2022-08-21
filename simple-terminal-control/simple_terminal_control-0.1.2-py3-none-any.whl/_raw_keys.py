from dataclasses import KW_ONLY, dataclass
from enum import Enum
from typing import Mapping, TypeAlias

from simple_terminal_control.position import TerminalPosition


@dataclass(frozen=True, kw_only=True)
class Delete:
    alt: bool


class Tab:
    pass


class Enter:
    pass


@dataclass(frozen=True)
class Arrow:
    class Direction(Enum):
        UP = 0
        DOWN = 1
        RIGHT = 2
        LEFT = 3

    direction: Direction
    _: KW_ONLY
    shift: bool
    alt: bool


@dataclass(frozen=True)
class Mouse:
    class Button(Enum):
        PRIMARY = 0
        SECONDARY = 1
        SCROLL_UP = 2
        SCROLL_DOWN = 3

        @property
        def is_scroll(self) -> bool:
            return self in (Mouse.Button.SCROLL_UP, Mouse.Button.SCROLL_DOWN)

        @property
        def is_clickable(self) -> bool:
            return self in (Mouse.Button.PRIMARY, Mouse.Button.SECONDARY)

    position: TerminalPosition
    button: Button
    _: KW_ONLY
    release: bool
    shift: bool
    cmd: bool


RawKey: TypeAlias = Delete | Tab | Enter | Arrow | Mouse


_ESC = "\x1b"
_CSI = _ESC + "["

_SEQUENCE_RAW_KEY_MAP: Mapping[str, RawKey] = {
    chr(127): Delete(alt=False),
    _ESC + chr(127): Delete(alt=True),
    "\t": Tab(),
    "\n": Enter(),
    _CSI + "A": Arrow(Arrow.Direction.UP, shift=False, alt=False),
    _CSI + "B": Arrow(Arrow.Direction.DOWN, shift=False, alt=False),
    _CSI + "C": Arrow(Arrow.Direction.RIGHT, shift=False, alt=False),
    _CSI + "D": Arrow(Arrow.Direction.LEFT, shift=False, alt=False),
    _CSI + "1;2A": Arrow(Arrow.Direction.UP, shift=True, alt=False),
    _CSI + "1;2B": Arrow(Arrow.Direction.DOWN, shift=True, alt=False),
    _CSI + "1;2C": Arrow(Arrow.Direction.RIGHT, shift=True, alt=False),
    _CSI + "1;2D": Arrow(Arrow.Direction.LEFT, shift=True, alt=False),
    _CSI + "1;9A": Arrow(Arrow.Direction.UP, shift=False, alt=True),
    _CSI + "1;9B": Arrow(Arrow.Direction.DOWN, shift=False, alt=True),
    _ESC + "f": Arrow(Arrow.Direction.RIGHT, shift=False, alt=True),
    _ESC + "b": Arrow(Arrow.Direction.LEFT, shift=False, alt=True),
    _CSI + "1;10A": Arrow(Arrow.Direction.UP, shift=True, alt=True),
    _CSI + "1;10B": Arrow(Arrow.Direction.DOWN, shift=True, alt=True),
    _CSI + "1;10C": Arrow(Arrow.Direction.RIGHT, shift=True, alt=True),
    _CSI + "1;10D": Arrow(Arrow.Direction.LEFT, shift=True, alt=True),
}

_CODE_RELEASE_MAP = {
    "m": True,
    "M": False,
}


def _parse_mouse_button(button_value: int):
    if button_value & ~0xE == 0:
        return Mouse.Button.SECONDARY if button_value & 0x2 > 0 else Mouse.Button.PRIMARY
    if button_value & ~0x4D == 0:
        return Mouse.Button.SCROLL_DOWN if button_value & 0x1 > 0 else Mouse.Button.SCROLL_UP
    return None


def raw_key_from_sequence(seq: str):
    if (raw_key := _SEQUENCE_RAW_KEY_MAP.get(seq)) is not None:
        return raw_key

    if seq.startswith(_CSI + "<"):
        try:
            code = seq[-1]
            button_value, col, row = list(map(int, seq[3:-1].split(";")))
            if (release := _CODE_RELEASE_MAP.get(code)) is not None:
                if (button := _parse_mouse_button(button_value)) is not None:
                    return Mouse(
                        TerminalPosition(row=row, col=col),
                        button,
                        release=release,
                        shift=button_value & 0x4 > 0,
                        cmd=button_value & 0x8 > 0,
                    )
        except ValueError:
            pass
    return None
