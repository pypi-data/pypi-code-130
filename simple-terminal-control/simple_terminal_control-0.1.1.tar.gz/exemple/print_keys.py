from argparse import ArgumentParser

from simple_terminal_control.keys import get_keys
from simple_terminal_control.util.debug import key_to_string


def main():
    parser = ArgumentParser()
    parser.add_argument("--mouse", action="store_true", help="Report mouse events")
    args = parser.parse_args()

    for key in get_keys(report_mouse=args.mouse):
        match key:
            case str():
                print(key, end="", flush=True)
            case _:
                print(key_to_string(key))


if __name__ == "__main__":
    main()
