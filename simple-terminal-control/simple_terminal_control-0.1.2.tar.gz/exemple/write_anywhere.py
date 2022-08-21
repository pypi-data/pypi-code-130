from simple_terminal_control.position import TerminalPosition, TerminalPositionDelta
from simple_terminal_control.keys import Arrow, Click, Delete, Scroll, Tab, Enter, get_keys


def main():
    cursor = TerminalPosition.get_cursor()
    for key in get_keys(report_mouse=True):
        match key:
            case str():
                print(key, end="", flush=True)
                cursor = cursor.add_chars(len(key))
            case Tab():
                print("\t", end="", flush=True)
                cursor = TerminalPosition.get_cursor()
            case Enter():
                print("\n", end="", flush=True)
                cursor = cursor.next_line()
            case Delete():
                value = 1
                if key.alt:
                    value = 4
                cursor = cursor.add_chars(-value)
                cursor.set_cursor()
                print(value * " ", end="", flush=True)
                cursor.set_cursor()
            case Arrow():
                value = 1
                if key.shift:
                    value = 4
                if key.alt:
                    value = 10000
                match key.direction:
                    case Arrow.Direction.UP:
                        cursor += TerminalPositionDelta(drow=-value, dcol=0)
                    case Arrow.Direction.DOWN:
                        cursor += TerminalPositionDelta(drow=value, dcol=0)
                    case Arrow.Direction.RIGHT:
                        cursor += TerminalPositionDelta(drow=0, dcol=value)
                    case Arrow.Direction.LEFT:
                        cursor += TerminalPositionDelta(drow=0, dcol=-value)
                cursor.set_cursor()
            case Click():
                if not key.secondary:
                    cursor = key.position
                cursor.set_cursor()
            case Scroll():
                value = 1
                if key.shift:
                    value = 2
                cursor += TerminalPositionDelta(drow=-value if key.down else value, dcol=0)
                cursor.set_cursor()
            case _:
                pass


if __name__ == "__main__":
    main()
