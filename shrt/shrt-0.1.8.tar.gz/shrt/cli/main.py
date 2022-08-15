from typer import Typer

from shrt.database import init_engine
from . import url

cli = Typer()
cli.add_typer(url.app, name='url')


@cli.callback()
def url_callback():
    init_engine()
