#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright 2022 Stéphane Caron
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Deploy and run Bazel targets on the Raspberry Pi.
"""

import argparse
import sys

from .find import find_file
from .run import run

__version__ = "0.1.0"


def get_workspace_name():
    workspace_file = find_file("WORKSPACE", required=True)
    print(f"workspace_file = {workspace_file}")
    for line in open(workspace_file, encoding="utf-8").readlines():
        if line.startswith('workspace(name = "'):
            return line.split('"')[1]
    raise ValueError(
        "Could not find name in WORKSPACE. "
        "Note that we don't parse Starlark beyond "
        '``workspace(name = "something")``.'
    )


def get_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(title="subcommands", dest="subcmd")

    # raspunzel run --------------------------------------------
    parser_run = subparsers.add_parser(
        "run",
        help="Run a Bazel target",
    )

    parser_run.add_argument("target", help="Bazel target")

    parser_run.add_argument(
        "subargs",
        nargs=argparse.REMAINDER,
        help="Arguments forwarded to the target.",
    )
    return parser


def main(argv=None):
    parser = get_argument_parser()
    args = parser.parse_args(argv)
    if args.subcmd is None:
        parser.print_help()
        sys.exit(-1)
    print(args)

    workspace_name = get_workspace_name()
    print(f"workspace_name = {workspace_name}")

    if args.subcmd == "run":
        run(workspace_name, args.target, args.subargs)
