import logging

import click
import treefiles as tf


@click.group()
def start_main_app():
    pass


@click.command()
def serve():
    from dash_cm.serve_local import serve_local

    click.secho("Starting local server...", fg="green", bold=True)
    serve_local()


@click.command()
@click.argument(
    "fname",
    type=click.Path(
        exists=True, file_okay=True, dir_okay=False, readable=True, resolve_path=True
    ),
)
def load(fname):
    from dash_cm.start_case import start_app

    click.secho(f"Loading case {fname!r}", fg="green", bold=True)
    start_app(fname)


start_main_app.add_command(serve)
start_main_app.add_command(load)


log = logging.getLogger("dashcm")

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    log = tf.get_logger()

    start_main_app()
