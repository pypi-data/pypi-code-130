from typer import Typer

from . import url

cli = Typer()
cli.add_typer(url.app, name='url')
