import sys

from . import __version__, bc, lang, tvm
from .exceptions import *


def compile(infile: str, outfile: str = "a.tvm") -> None:
    p = lang.Parser(infile)
    hc = p.gen_hc()
    try:
        bc.write_hc_file(outfile, hc)
    except TASM_IntSizeToBigError as e:
        print(f"Error: {e}")


def run(infile: str) -> None:
    p = tvm.Program(infile)
    return p.run()


def usage() -> None:
    print("\nUsage:")
    print("\ttasm help [command]             - Show documentation.")
    print("\ttasm version                    - Shows the current version.")
    print("\ttasm compile <infile> [outfile] - Compiles a tasm program.")
    print("\ttasm run <file>                 - Run a tvm program.")


def help_(command: str) -> None:
    match command:
        case "compile":
            print("Compiles a tasm file to a tvm program.")

        case "run":
            print("Runs a tvm program.")

        case _:
            print("Unknown command.")


def main() -> None:
    argv = sys.argv[1:]

    match argv:
        # compile
        case ["compile", infile]:
            compile(infile)

        case ["compile", infile, ("-o" | "--output"), outfile]:
            compile(infile, outfile)

        # run
        case ["run", infile]:
            return run(infile)

        # help
        case ["help"]:
            print("Compile or run a tasm program with tasm.")
            print("Run 'tasm help <command>' for more documentation.")
            usage()

        case ["help", command]:
            help_(command)

        # version
        case ["version"]:
            print(f"tasm {__version__}")

        #
        case _:
            print("Error: no command given.")
            usage()
