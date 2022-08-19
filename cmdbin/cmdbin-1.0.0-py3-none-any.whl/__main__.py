#!/usr/bin/env python3
from argparse import ArgumentParser, FileType
import sys

import cmdbin.v1


def main():
    parser = ArgumentParser(description="cmdbin 1.0.0. - https://github.com/blucobalt/cmdbin.py")
    parser.add_argument("--input", "-i", help="name of the file to upload, or \"-\" for stdin. defaults to stdin",
                        default="-", type=FileType("r"))
    parser.add_argument("--passthrough", "-p", help="passthrough lines from stdin to stdout",
                        action="store_true")
    parser.add_argument("--slugonly", "-s", help="only return the slug, not the full link",
                        action="store_true")
    parser.add_argument("--raw", "-r", help="return the link for the raw paste", action="store_true")
    parser.add_argument("--endpoint", "-e", help="specify a specific cmdbin endpoint. defaults to https://cmdbin.cc.",
                        default="https://cmdbin.cc")
    args = parser.parse_args()

    buffer: list = []
    try:
        for line in args.input:
            buffer.append(line)
            if args.passthrough:
                sys.stdout.write(line)
    except KeyboardInterrupt:
        sys.exit(1)
    args.input.close()

    status, response = cmdbin.v1.new_slugonly("".join(buffer), args.endpoint) if args.slugonly else cmdbin.v1.new(
        "".join(buffer), args.endpoint)
    if status == 200:
        print(response)
        sys.exit(0)
    elif status == 413:
        print("error: payload too big. max size is 512kb.")
        sys.exit(1)
    else:
        print("error returned from server: " + status)
        sys.exit(1)


if __name__ == "__main__":
    main()
