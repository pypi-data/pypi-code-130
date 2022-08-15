import argparse
import os

from . import __version__, delta_env_str, get_base_env, get_post_env

HEADER = 15 * "=" + os.linesep + "delta_env {:s}".format(__version__) + os.linesep + 15 * "="


def delta_env_command_line() -> int:

    parser = argparse.ArgumentParser(
        description="A tool to analyze how a shell script modifies environment variables.",
        epilog="Do NOT run as root, and do NOT run scripts of unknown/unstrusted sources!",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument("--version", action="version", version=__version__)

    parser.add_argument(
        "payload",
        metavar="payload",
        type=str,
        help='Target script to be executed as "source <payload>". You may use arguments as well.',
    )

    parser.add_argument(
        "--join-paths",
        action="store_true",
        help="Do not show multiple paths seperately, instead join them with path seperator",
    )

    parser.add_argument(
        "--shell",
        metavar="shell",
        type=str,
        default=os.environ.get("SHELL"),
        help="Specify a different shell executable, default is read from $SHELL",
    )

    parser.add_argument(
        "--from-current",
        action="store_true",
        help="Use the current environment as the base environment",
    )

    args = parser.parse_args()

    # Supplied script (payload) may have arguments, extract filename and check if it exists
    filename = args.payload.split()[0]
    if not os.path.isfile(filename):
        print("Given payload {:s} does not exist!".format(filename))
        return 1

    base_env = dict(os.environ) if args.from_current else get_base_env(shell=args.shell)
    post_env = get_post_env(args.payload, shell=args.shell, login_shell=not args.from_current)

    print(HEADER)
    print("Executed command: \"source {:s} > /dev/null\"".format(args.payload))
    print("Shell: {:s}".format(args.shell) + os.linesep)
    print(delta_env_str(base_env, post_env, show_added_paths_seperately=not args.join_paths))

    return 0
