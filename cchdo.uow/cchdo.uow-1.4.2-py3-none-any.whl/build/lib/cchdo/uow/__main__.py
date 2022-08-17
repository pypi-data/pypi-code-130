import click

from . import __version__
from . import check_apikey

from .init import do_init
from .list import do_list
from .bootstrap import do_bootstrap
from .fetch import do_fetch
from .status import do_status
from .commit import do_commit
from .info import do_info


@click.group()
@click.version_option(__version__, prog_name="uow")
def cli():
    """The uow command creates and manipulates CCHDO uow directories

    For documentation, see the `uow man` subcommand
    """
    pass


@cli.command(help=do_bootstrap.__doc__)
def bootstrap():
    do_bootstrap()


@cli.command(help=do_init.__doc__)
@click.option(
    "-e",
    "--expocode",
    prompt="Expocode of the cruise",
    help="the cruise to associate with uow",
)
@click.option(
    "-d",
    "--dir-name",
    prompt="Directory name for the uow",
    help="what to name the uow dir",
)
def init(expocode, dir_name):
    check_apikey()
    do_init(expocode, dir_name)


@cli.command(help=do_list.__doc__)
@click.option(
    "-t",
    "--type",
    type=click.Choice(["all", "dataset", "unprocessed", "merged", "other"]),
    default="all",
)
def list(type):
    do_list(type)


@cli.command(help=do_fetch.__doc__)
@click.argument("file_ids", nargs=-1, type=int)
@click.option("-p", "--panic", is_flag=True, help="Uhoh, better grab everything")
@click.option(
    "-e",
    "--external",
    is_flag=True,
    help="Allow the fetching of files not attached to this cruise",
)
def fetch(file_ids, panic, external):
    check_apikey()
    do_fetch(file_ids, panic, external)


@cli.command(help=do_status.__doc__)
def status():
    do_status()


@cli.command(help=do_info.__doc__)
@click.argument("file_id", nargs=1, type=int)
def info(file_id):
    do_info(file_id)


@cli.command(help=do_commit.__doc__)
def commit():
    check_apikey()
    do_commit()


@cli.command()
def man():
    """Show the manual page for the uow command"""
    from importlib.resources import path
    from subprocess import run

    with path("cchdo.uow", "uow.1") as man:
        run(["man", man])


if __name__ == "__main__":
    cli()
