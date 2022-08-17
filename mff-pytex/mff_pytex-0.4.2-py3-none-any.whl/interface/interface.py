"""Interface module."""
import click
import mff_pytex


@click.group()
@click.version_option(mff_pytex.__version__)
@click.pass_context
def cli(ctx):
    pass
