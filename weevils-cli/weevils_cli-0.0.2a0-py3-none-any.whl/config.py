import json
import sys
from typing import IO, Any, Iterable, Optional, Union

import click
from tabulate import tabulate
from weevils import WeevilsClient, from_env
from weevils.models import WeevilsCore


def make_client() -> WeevilsClient:
    return from_env()


def write_table(rows: Iterable[Any], headers: Optional[Iterable[str]] = None, stream: IO = None):
    stream = stream or sys.stdout
    formatted = tabulate(rows, headers=headers, tablefmt="simple")
    stream.write(formatted)
    stream.write("\n")
    stream.flush()


def dump_json(something: Union[WeevilsCore, Iterable], exit: bool = True):
    try:
        click.echo(json.dumps([obj for obj in iter(something)]))
    except TypeError:
        click.echo(json.dumps(something.raw, indent=2))

    if exit:
        sys.exit(0)
