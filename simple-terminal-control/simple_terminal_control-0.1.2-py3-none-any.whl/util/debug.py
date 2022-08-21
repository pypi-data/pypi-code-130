import sys

from simple_terminal_control.keys import Arrow, Click, Delete, Drag, Enter, Key, Scroll, Tab
from simple_terminal_control.position import TerminalPosition


_ASCII_DESCRIPTION = {
    0: "Null character",
    1: "Start of Heading",
    2: "Start of Text",
    3: "End of Text",
    4: "End of Transmission",
    5: "Enquiry",
    6: "Acknowledge",
    7: "Bell",
    8: "Backspace",
    9: "Horizontal Tab",
    10: "Line Feed",
    11: "Vertical Tab",
    12: "Form Feed",
    13: "Carriage Return",
    14: "Shift Out",
    15: "Shift In",
    16: "Data Link Escape",
    17: "Device Control 1",
    18: "Device Control 2",
    19: "Device Control 3",
    20: "Device Control 4",
    21: "Negative Acknowledge",
    22: "Synchronous Idle",
    23: "End of Transmit Block",
    24: "Cancel",
    25: "End of Medium",
    26: "Substitute",
    27: "Escape",
    28: "File Separator",
    29: "Group Separator",
    30: "Record Separator",
    31: "Unit Separator",
    32: "Space",
    127: "Delete",
}


def _format_char(char: str):
    o = ord(char)
    if 33 <= o <= 126:
        return char
    elif o in _ASCII_DESCRIPTION:
        return f"<{_ASCII_DESCRIPTION[o].lower()}>"
    else:
        return f"<U+{o}>"


def print_string(s: str):
    sys.stdout.write("\n")
    sys.stdout.write("".join(_format_char(c) for c in s))


def _position_to_string(pos: TerminalPosition):
    return f"{pos.row} {pos.col}"


def _mouse_modifier_to_string(*, shift: bool, ctrl: bool):
    return (" SHIFT" if shift else "") + (" CMD" if ctrl else "")


def _click_secondary_to_string(secondary: bool):
    return "RIGHT " if secondary else ""


def key_to_string(key: Key):
    match key:
        case Delete():
            return f"<DEL{' ALT' if key.alt else ''}>"
        case Tab():
            return "<TAB>"
        case Enter():
            return "<NEWLINE>"
        case Arrow():
            modifiers = (" SHIFT" if key.shift else "") + (" ALT" if key.alt else "")
            match key.direction:
                case Arrow.Direction.UP:
                    return f"<UP{modifiers}>"
                case Arrow.Direction.DOWN:
                    return f"<DOWN{modifiers}>"
                case Arrow.Direction.RIGHT:
                    return f"<RIGHT{modifiers}>"
                case Arrow.Direction.LEFT:
                    return f"<LEFT{modifiers}>"
        case Click():
            modifiers = _mouse_modifier_to_string(shift=key.shift, ctrl=key.ctrl)
            secondary = _click_secondary_to_string(key.secondary)
            return f"<{secondary}CLICK {_position_to_string(key.position)}{modifiers}>"
        case Drag():
            modifiers = _mouse_modifier_to_string(shift=key.shift, ctrl=key.ctrl)
            secondary = _click_secondary_to_string(key.secondary)
            origin = _position_to_string(key.origin)
            position = _position_to_string(key.position)
            return f"<{secondary}DRAG FROM {origin} TO {position}{modifiers}>"
        case Scroll():
            modifiers = _mouse_modifier_to_string(shift=key.shift, ctrl=key.ctrl)
            direction = "DOWN" if key.down else "UP"
            return f"<SCROLL {direction} {_position_to_string(key.position)}{modifiers}>"
