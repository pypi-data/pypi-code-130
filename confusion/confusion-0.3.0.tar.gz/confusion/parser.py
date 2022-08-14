#! /usr/bin/env python
# encoding: utf-8

# Copyright (C) 2022 tundish

# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.

# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301
# USA

"""
This utility applies configparser substitution patterns as a preprocessor
for, eg: TOML files.

Usage:

    python -m confusion.parser my.ini > my.toml

"""


import argparse
import configparser
import itertools
import pathlib
import re
import sys

try:
    import tomllib
except ImportError:
    import tomli as tomllib


class TOMLParser(configparser.ConfigParser):

    @classmethod
    def from_string(cls, text, **kwargs):
        rv = cls(**kwargs)
        rv.read_string(text)
        return rv

    def __init__(self, *args, interpolation=None, **kwargs):
        interpolation = interpolation or configparser.ExtendedInterpolation()
        super().__init__(interpolation=interpolation, **kwargs)
        self.SECTCRE = re.compile("\[\s*(?P<header>\S+)\s*\]")
        self.optionxform = str

    @property
    def sections(self):
        return {k: v for k, v in self.items() if k != self.default_section}

    @property
    def literals(self):
        d = self.defaults()
        return {k: dict(d, **s) for k, s in self.sections.items()}

    @property
    def tables(self):
        text = self.write_string()
        return tomllib.loads(text)

    def write_string(self):
        rv = [
            itertools.chain(
                (f"[{l}]",),
                (f"{k} = {v}" for k, v in s.items())
            )
            for l, s in self.literals.items()
        ]
        return "\n".join(j for i in rv for j in i)


def main(args):
    if not args.input:
        text = sys.stdin.read()
    else:
        text = args.input.read_text()

    conf = TOMLParser.from_string(text)
    print(conf.write_string(), file=sys.stdout)


def parser():
    rv = argparse.ArgumentParser(__doc__)
    rv.add_argument(
        "input", nargs="?", type=pathlib.Path,
        help="Set input file."
    )
    return rv


def run():
    p = parser()
    args = p.parse_args()
    rv = main(args)
    sys.exit(rv)


if __name__ == "__main__":
    run()
