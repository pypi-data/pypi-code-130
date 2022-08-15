import argparse
import anton_cli

# def parser_func():
parser = argparse.ArgumentParser()

# Adding arguments
parser.add_argument(
    "--string",
    type=str,
    help="Input a string"
)

parser.add_argument(
    "--file",
    type=str,
    help="Input a file path"
)


def select_action(args):
    if args.file and args.string:
        return anton_cli.read_from_file(args.file)
    if args.string:
        return anton_cli.split_letters(args.string)
    elif args.file:
        return anton_cli.read_from_file(args.file)


if __name__ == "__main__":
    # Parsing arguments
    args = parser.parse_args()
    select_action(args)
