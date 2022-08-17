#!/usr/bin/env python


from argparse import ArgumentParser
from sharpai_hub.commands.user import UserCommands
from sharpai_hub.commands.device import DeviceCommands

def main():
    parser = ArgumentParser(
        "sharpai-cli", usage="sharpai-cli <command> [<args>]"
    )
    commands_parser = parser.add_subparsers(help="sharpai-cli command helpers")

    # Register commands
    UserCommands.register_subcommand(commands_parser)
    DeviceCommands.register_subcommand(commands_parser)

    # Let's go
    args = parser.parse_args()

    if not hasattr(args, "func"):
        parser.print_help()
        exit(1)

    # Run
    service = args.func(args)
    service.run()


if __name__ == "__main__":
    main()