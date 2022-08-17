# -*- coding: utf-8 -*-

from __future__ import annotations

import warnings

import click

from .compiler import FileCompiler


@click.command()
@click.option("--dump", "-d", help="Dump the compiled AST to a file.")
@click.argument("file", type=click.Path(exists=True))
def start(file: str, dump: None | str = None) -> None:
    """FILE: The file to compile."""

    with open(file, "r") as fp:
        source = fp.read()

    warnings.simplefilter("ignore")
    compiler = FileCompiler(source, True if dump else False, dump)
    compiler.start()
